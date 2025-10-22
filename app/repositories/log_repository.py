from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import logging
from elasticsearch import Elasticsearch, NotFoundError
from app.core.config import settings
from app.schemas.log import PIIDetectionLog, LogSearchRequest, LogSearchResponse, LogStatsResponse

logger = logging.getLogger(__name__)

class LogRepository:
    """Elasticsearch 기반 로그 저장소"""
    
    def __init__(self):
        self.es_client: Optional[Elasticsearch] = None
        self.index_name = f"{settings.ELASTICSEARCH_INDEX_PREFIX}-logs"
        self._init_elasticsearch()
    
    def _init_elasticsearch(self):
        """Elasticsearch 클라이언트 초기화"""
        try:
            es_config = {
                "hosts": [settings.ELASTICSEARCH_URL],
                "verify_certs": False,
                "request_timeout": 30,
            }
            print(f"DEBUG: Attempting to connect to Elasticsearch at: {settings.ELASTICSEARCH_URL}") # DEBUG PRINT
            
            # 인증 정보가 있으면 추가
            if settings.ELASTICSEARCH_USERNAME and settings.ELASTICSEARCH_PASSWORD:
                es_config["basic_auth"] = (settings.ELASTICSEARCH_USERNAME, settings.ELASTICSEARCH_PASSWORD)
            
            self.es_client = Elasticsearch(**es_config)
            
            # 연결 테스트
            if self.es_client.ping():
                logger.info(f"Elasticsearch connected: {settings.ELASTICSEARCH_URL}")
                self._create_index_if_not_exists()
            else:
                self.es_client = None
                raise ConnectionError("Failed to connect to Elasticsearch. Please check the connection and settings.")
                
        except Exception as e:
            self.es_client = None
            raise ConnectionError(f"Failed to initialize Elasticsearch: {str(e)}")
    
    def _create_index_if_not_exists(self):
        """인덱스가 없으면 생성"""
        try:
            if not self.es_client.indices.exists(index=self.index_name):
                mapping = {
                    "mappings": {
                        "properties": {
                            "timestamp": {"type": "date"},
                            "client_ip": {"type": "ip"},
                            "input_text": {
                                "type": "text",
                                "analyzer": "korean"
                            },
                            "has_pii": {"type": "boolean"},
                            "entity_types": {"type": "keyword"},
                            "processing_time_ms": {"type": "float"},
                            "level": {"type": "keyword"},
                            "request_id": {"type": "keyword"},
                            "user_agent": {"type": "text"},
                            "detected_entities": {
                                "type": "nested",
                                "properties": {
                                    "type": {"type": "keyword"},
                                    "value": {"type": "text"},
                                    "confidence": {"type": "float"}
                                }
                            }
                        }
                    },
                    "settings": {
                        "number_of_shards": 1,
                        "number_of_replicas": 0,
                        "analysis": {
                            "analyzer": {
                                "korean": {
                                    "type": "standard"
                                }
                            }
                        }
                    }
                }
                
                self.es_client.indices.create(index=self.index_name, body=mapping)
                logger.info(f"Created Elasticsearch index: {self.index_name}")
                
        except Exception as e:
            logger.error(f"Failed to create index: {str(e)}")
    
    async def save_log(self, log: PIIDetectionLog) -> bool:
        """로그를 Elasticsearch에 저장"""
        if not self.es_client:
            raise ConnectionError("Elasticsearch client is not available. Log was not saved.")
        
        try:
            # 고유 ID 생성
            if not log.id:
                log.id = str(uuid.uuid4())
            
            # 문서 저장
            doc = log.model_dump()
            response = self.es_client.index(
                index=self.index_name,
                id=log.id,
                body=doc
            )
            
            logger.debug(f"Log saved to ES: {log.id}")
            return response.get("result") in ["created", "updated"]
            
        except Exception as e:
            logger.error(f"Failed to save log to Elasticsearch: {str(e)}")
            return False
    
    async def get_log_by_id(self, log_id: str) -> Optional[PIIDetectionLog]:
        """ID로 단일 로그 조회"""
        if not self.es_client:
            logger.warning("Elasticsearch client not available")
            return None
        
        try:
            response = self.es_client.get(index=self.index_name, id=log_id)
            source = response["_source"]
            source["id"] = response["_id"]
            return PIIDetectionLog(**source)
        except NotFoundError:
            logger.warning(f"Log with id '{log_id}' not found.")
            return None
        except Exception as e:
            logger.error(f"Failed to get log by id: {str(e)}")
            return None
    
    async def search_logs(self, search_request: LogSearchRequest) -> LogSearchResponse:
        """로그 검색"""
        if not self.es_client:
            logger.warning("Elasticsearch client not available")
            return LogSearchResponse(
                logs=[], total=0, page=search_request.page, 
                size=search_request.size, total_pages=0
            )
        
        try:
            # 검색 쿼리 구성
            query = self._build_search_query(search_request)
            
            # 페이징 계산
            from_index = (search_request.page - 1) * search_request.size
            
            # 검색 실행
            response = self.es_client.search(
                index=self.index_name,
                body={
                    "query": query,
                    "from": from_index,
                    "size": search_request.size,
                    "sort": [{search_request.sort_by: {"order": search_request.sort_order}}]
                }
            )
            
            # 결과 파싱
            hits = response.get("hits", {})
            total = hits.get("total", {}).get("value", 0)
            total_pages = (total + search_request.size - 1) // search_request.size
            
            logs = []
            for hit in hits.get("hits", []):
                source = hit["_source"]
                source["id"] = hit["_id"]
                logs.append(PIIDetectionLog(**source))
            
            # 통계 계산
            stats = await self._calculate_stats(search_request)
            
            return LogSearchResponse(
                logs=logs,
                total=total,
                page=search_request.page,
                size=search_request.size,
                total_pages=total_pages,
                stats=stats
            )
            
        except Exception as e:
            logger.error(f"Failed to search logs: {str(e)}")
            return LogSearchResponse(
                logs=[], total=0, page=search_request.page,
                size=search_request.size, total_pages=0
            )
    
    def _build_search_query(self, search_request: LogSearchRequest) -> Dict[str, Any]:
        """검색 쿼리 구성"""
        must_conditions = []
        
        # 시간 범위 필터
        if search_request.start_time or search_request.end_time:
            time_range = {}
            if search_request.start_time:
                time_range["gte"] = search_request.start_time.isoformat()
            if search_request.end_time:
                time_range["lte"] = search_request.end_time.isoformat()
            
            must_conditions.append({
                "range": {"timestamp": time_range}
            })
        
        # 클라이언트 IP 필터
        if search_request.client_ip:
            must_conditions.append({
                "term": {"client_ip": search_request.client_ip}
            })
        
        # PII 탐지 여부 필터
        if search_request.has_pii is not None:
            must_conditions.append({
                "term": {"has_pii": search_request.has_pii}
            })
        
        # 엔티티 타입 필터
        if search_request.entity_types:
            must_conditions.append({
                "terms": {"entity_types": search_request.entity_types}
            })
        
        # 로그 레벨 필터
        if search_request.level:
            must_conditions.append({
                "term": {"level": search_request.level.value}
            })
        
        # 텍스트 검색
        if search_request.search_text:
            must_conditions.append({
                "match": {"input_text": search_request.search_text}
            })
        
        # 쿼리 구성
        if must_conditions:
            query = {"bool": {"must": must_conditions}}
        else:
            query = {"match_all": {}}
        
        return query
    
    async def _calculate_stats(self, search_request: LogSearchRequest) -> Dict[str, Any]:
        """통계 정보 계산"""
        try:
            # 전체 쿼리로 집계
            query = self._build_search_query(search_request)
            
            agg_query = {
                "query": query,
                "aggs": {
                    "pii_stats": {
                        "terms": {"field": "has_pii"}
                    },
                    "entity_type_stats": {
                        "terms": {"field": "entity_types", "size": 10}
                    },
                    "avg_processing_time": {
                        "avg": {"field": "processing_time_ms"}
                    },
                    "hourly_stats": {
                        "date_histogram": {
                            "field": "timestamp",
                            "calendar_interval": "hour",
                            "format": "yyyy-MM-dd HH:mm"
                        }
                    }
                },
                "size": 0
            }
            
            response = self.es_client.search(
                index=self.index_name,
                body=agg_query
            )
            
            aggs = response.get("aggregations", {})
            
            # PII 탐지 통계
            pii_stats = {}
            for bucket in aggs.get("pii_stats", {}).get("buckets", []):
                pii_stats[str(bucket["key"])] = bucket["doc_count"]
            
            # 엔티티 타입 통계
            entity_type_stats = {}
            for bucket in aggs.get("entity_type_stats", {}).get("buckets", []):
                entity_type_stats[bucket["key"]] = bucket["doc_count"]
            
            # 시간별 통계
            hourly_stats = {}
            for bucket in aggs.get("hourly_stats", {}).get("buckets", []):
                hourly_stats[bucket["key_as_string"]] = bucket["doc_count"]
            
            return {
                "pii_stats": pii_stats,
                "entity_type_stats": entity_type_stats,
                "hourly_stats": hourly_stats,
                "avg_processing_time": aggs.get("avg_processing_time", {}).get("value", 0)
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate stats: {str(e)}")
            return {}
    
    async def get_stats(self, days: int = 7) -> LogStatsResponse:
        """로그 통계 조회"""
        if not self.es_client:
            return LogStatsResponse(
                total_logs=0, pii_detected_count=0, pii_detection_rate=0.0,
                entity_type_stats={}, hourly_stats={}, avg_processing_time=0.0,
                top_ips=[]
            )
        
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            query = {
                "bool": {
                    "must": [
                        {
                            "range": {
                                "timestamp": {
                                    "gte": start_time.isoformat(),
                                    "lte": end_time.isoformat()
                                }
                            }
                        }
                    ]
                }
            }
            
            agg_query = {
                "query": query,
                "aggs": {
                    "total_logs": {"value_count": {"field": "id"}},
                    "pii_detected": {
                        "filter": {"term": {"has_pii": True}},
                        "aggs": {"count": {"value_count": {"field": "id"}}}
                    },
                    "entity_types": {
                        "terms": {"field": "entity_types", "size": 20}
                    },
                    "hourly_stats": {
                        "date_histogram": {
                            "field": "timestamp",
                            "calendar_interval": "hour"
                        }
                    },
                    "avg_processing_time": {
                        "avg": {"field": "processing_time_ms"}
                    },
                    "top_ips": {
                        "terms": {"field": "client_ip", "size": 10}
                    }
                },
                "size": 0
            }
            
            response = self.es_client.search(
                index=self.index_name,
                body=agg_query
            )
            
            aggs = response.get("aggregations", {})
            
            total_logs = aggs.get("total_logs", {}).get("value", 0)
            pii_detected_count = aggs.get("pii_detected", {}).get("count", {}).get("value", 0)
            pii_detection_rate = (pii_detected_count / total_logs * 100) if total_logs > 0 else 0.0
            
            # 엔티티 타입별 통계
            entity_type_stats = {}
            for bucket in aggs.get("entity_types", {}).get("buckets", []):
                entity_type_stats[bucket["key"]] = bucket["doc_count"]
            
            # 시간별 통계
            hourly_stats = {}
            for bucket in aggs.get("hourly_stats", {}).get("buckets", []):
                hourly_stats[bucket["key_as_string"]] = bucket["doc_count"]
            
            # 상위 IP들
            top_ips = []
            for bucket in aggs.get("top_ips", {}).get("buckets", []):
                top_ips.append({
                    "ip": bucket["key"],
                    "count": bucket["doc_count"]
                })
            
            return LogStatsResponse(
                total_logs=total_logs,
                pii_detected_count=pii_detected_count,
                pii_detection_rate=pii_detection_rate,
                entity_type_stats=entity_type_stats,
                hourly_stats=hourly_stats,
                avg_processing_time=aggs.get("avg_processing_time", {}).get("value", 0.0),
                top_ips=top_ips
            )
            
        except Exception as e:
            logger.error(f"Failed to get stats: {str(e)}")
            return LogStatsResponse(
                total_logs=0, pii_detected_count=0, pii_detection_rate=0.0,
                entity_type_stats={}, hourly_stats={}, avg_processing_time=0.0,
                top_ips=[]
            )

    async def count_blocks_since(self, start_time: datetime) -> int:
        """특정 시간 이후의 차단 로그 개수를 집계"""
        if not self.es_client:
            logger.warning("Elasticsearch client not available, returning 0")
            return 0
        
        try:
            query = {
                "bool": {
                    "must": [
                        {
                            "range": {
                                "timestamp": {
                                    "gte": start_time.isoformat()
                                }
                            }
                        },
                        {
                            "term": {
                                "metadata.action.keyword": "BLOCK"
                            }
                        }
                    ]
                }
            }
            
            response = self.es_client.count(
                index=self.index_name,
                body={"query": query}
            )
            
            return response.get("count", 0)
            
        except Exception as e:
            logger.error(f"Failed to count blocked logs: {str(e)}")
            return 0

# 싱글톤 인스턴스
_log_repository_instance: Optional[LogRepository] = None

def get_log_repository() -> LogRepository:
    """로그 저장소 싱글톤 인스턴스 반환"""
    global _log_repository_instance
    if _log_repository_instance is None:
        _log_repository_instance = LogRepository()
    return _log_repository_instance



