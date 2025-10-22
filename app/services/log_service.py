import logging
from typing import Optional
from datetime import datetime, timedelta
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

#깃 커밋 확인용