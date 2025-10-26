import logging
from typing import Optional, Dict
from datetime import datetime, timedelta
import pytz

from app.schemas.dashboard import (
    DashboardSummaryResponse,
    DashboardOverview,
    RealTimeStats,
    QuarterlyStat,
)
from app.schemas.log import PIIDetectionLog, LogSearchRequest, LogSearchResponse, LogStatsResponse
from app.repositories.log_repository import get_log_repository

logger = logging.getLogger(__name__)

class LogService:
    """로그 조회 비즈니스 로직을 처리하는 서비스"""
    
    def __init__(self):
        self.log_repository = get_log_repository()
    
    async def search_logs(self, search_request: LogSearchRequest) -> LogSearchResponse:
        """로그 검색"""
        try:
            logger.info(f"Searching logs with filters: {search_request.model_dump()}")
            
            # 기본 시간 범위 설정 (24시간)
            if not search_request.start_time and not search_request.end_time:
                search_request.end_time = datetime.now()
                search_request.start_time = search_request.end_time - timedelta(hours=24)
            
            result = await self.log_repository.search_logs(search_request)
            
            logger.info(f"Found {result.total} logs matching criteria")
            return result
            
        except Exception as e:
            logger.error(f"Failed to search logs: {str(e)}")
            return LogSearchResponse(
                logs=[], total=0, page=search_request.page,
                size=search_request.size, total_pages=0
            )
    
    async def get_log_by_id(self, log_id: str) -> Optional[PIIDetectionLog]:
        """ID로 단일 로그 조회"""
        try:
            logger.info(f"Fetching log with id: {log_id}")
            log = await self.log_repository.get_log_by_id(log_id)
            if not log:
                logger.warning(f"Log with id '{log_id}' not found in service.")
            return log
        except Exception as e:
            logger.error(f"Failed to get log by id in service: {str(e)}")
            return None
    
    async def get_stats(self, days: int = 7) -> LogStatsResponse:
        """로그 통계 조회"""
        try:
            logger.info(f"Getting log stats for last {days} days")
            
            stats = await self.log_repository.get_stats(days)
            
            logger.info(f"Stats retrieved: total_logs={stats.total_logs}, pii_rate={stats.pii_detection_rate:.1f}%")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get log stats: {str(e)}")
            return LogStatsResponse(
                total_logs=0, pii_detected_count=0, pii_detection_rate=0.0,
                entity_type_stats={}, hourly_stats={}, avg_processing_time=0.0,
                top_ips=[]
            )
    
    async def get_recent_logs(self, limit: int = 50) -> LogSearchResponse:
        """최근 로그 조회"""
        try:
            search_request = LogSearchRequest(
                start_time=datetime.now() - timedelta(hours=24),
                end_time=datetime.now(),
                page=1,
                size=limit
            )
            
            return await self.search_logs(search_request)
            
        except Exception as e:
            logger.error(f"Failed to get recent logs: {str(e)}")
            return LogSearchResponse(
                logs=[], total=0, page=1,
                size=limit, total_pages=0
            )

    async def get_block_count_since(self, start_time: datetime) -> int:
        """특정 시간 이후의 차단 로그 개수를 조회합니다."""
        try:
            logger.info(f"Counting blocked logs since {start_time.isoformat()}")
            count = await self.log_repository.count_blocks_since(start_time)
            return count
        except Exception as e:
            logger.error(f"Failed to count blocked logs in service: {str(e)}")
            return 0

    async def get_dashboard_summary(
        self,
        days: int,
        tz: str,
        recent_limit: int,
    ) -> DashboardSummaryResponse:
        """대시보드에 필요한 요약 데이터를 반환"""
        client_tz = pytz.timezone(tz)
        end_time = datetime.utcnow().replace(tzinfo=pytz.utc)
        start_time = end_time - timedelta(days=days)

        aggs = await self.log_repository.get_dashboard_summary_stats(start_time, end_time)
        recent_logs = await self.log_repository.get_recent_detections(limit=recent_limit)

        total_logs = int(aggs.get("total_logs", {}).get("value", 0))
        pii_detected_count = int(aggs.get("pii_detected", {}).get("doc_count", 0))
        pii_detection_rate = (
            (pii_detected_count / total_logs * 100.0) if total_logs > 0 else 0.0
        )

        entity_type_stats = {
            bucket.get("key"): int(bucket.get("doc_count", 0))
            for bucket in aggs.get("entity_types", {}).get("buckets", [])
            if bucket.get("key")
        }

        hourly_stats: Dict[str, int] = {}
        hourly_buckets = aggs.get("hourly_stats", {}).get("buckets", [])
        for bucket in hourly_buckets:
            dt = datetime.utcfromtimestamp(bucket.get("key", 0) / 1000.0).replace(tzinfo=pytz.utc)
            localized = dt.astimezone(client_tz)
            label = localized.strftime("%Y-%m-%d %H:%M")
            hourly_stats[label] = int(bucket.get("doc_count", 0))

        total_last_hour = 0
        if hourly_buckets:
            total_last_hour = int(hourly_buckets[-1].get("doc_count", 0))

        quarterly_stats = []
        for bucket in aggs.get("quarterly_stats", {}).get("buckets", []):
            dt = datetime.utcfromtimestamp(bucket.get("key", 0) / 1000.0).replace(tzinfo=pytz.utc)
            localized = dt.astimezone(client_tz)
            quarter = (localized.month - 1) // 3 + 1
            label = f"{localized.year}-Q{quarter}"
            pii_in_quarter = int(bucket.get("pii_detected", {}).get("doc_count", 0))
            quarterly_stats.append(
                QuarterlyStat(
                    label=label,
                    total_count=int(bucket.get("doc_count", 0)),
                    pii_detected_count=pii_in_quarter,
                )
            )

        top_ips = [
            {"ip": bucket.get("key"), "count": int(bucket.get("doc_count", 0))}
            for bucket in aggs.get("top_ips", {}).get("buckets", [])
            if bucket.get("key")
        ]

        label_action_breakdown: Dict[str, Dict[str, int]] = {}
        for bucket in aggs.get("label_action_breakdown", {}).get("buckets", []):
            label = bucket.get("key")
            if not label:
                continue
            actions = {
                action_bucket.get("key"): int(action_bucket.get("doc_count", 0))
                for action_bucket in bucket.get("actions", {}).get("buckets", [])
                if action_bucket.get("key")
            }
            label_action_breakdown[label] = actions

        log_status_stats = {
            bucket.get("key"): int(bucket.get("doc_count", 0))
            for bucket in aggs.get("log_status_stats", {}).get("buckets", [])
            if bucket.get("key")
        }

        project_stats = [
            {"project": bucket.get("key"), "count": int(bucket.get("doc_count", 0))}
            for bucket in aggs.get("project_stats", {}).get("buckets", [])
            if bucket.get("key")
        ]

        ai_service_stats = {
            bucket.get("key"): int(bucket.get("doc_count", 0))
            for bucket in aggs.get("ai_service_stats", {}).get("buckets", [])
            if bucket.get("key")
        }

        overview = DashboardOverview(
            total_logs=total_logs,
            pii_detected_count=pii_detected_count,
            pii_detection_rate=pii_detection_rate,
        )

        real_time = RealTimeStats(
            hourly_counts=hourly_stats,
            total_last_hour=total_last_hour,
            timezone=tz,
            last_updated=datetime.now(client_tz),
        )

        return DashboardSummaryResponse(
            overview=overview,
            real_time=real_time,
            quarterly_stats=quarterly_stats,
            top_ips=top_ips,
            label_stats=entity_type_stats,
            label_action_breakdown=label_action_breakdown,
            log_status_stats=log_status_stats,
            project_stats=project_stats,
            detections=recent_logs,
            ai_service_stats=ai_service_stats,
            timezone=tz,
            range_days=days,
        )

#깃 커밋 확인용
