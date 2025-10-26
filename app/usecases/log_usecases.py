from fastapi import Depends
from typing import Optional
from app.services.log_service import LogService
from app.schemas.log import PIIDetectionLog, LogSearchRequest, LogSearchResponse, LogStatsResponse

class LogUseCase:
    """로그 관련 유스케이스를 처리하는 클래스"""
    
    def __init__(self, log_service: LogService = Depends()):
        self.log_service = log_service
    
    async def get_log_by_id(self, log_id: str) -> Optional[PIIDetectionLog]:
        """ID로 단일 로그 조회 유스케이스"""
        return await self.log_service.get_log_by_id(log_id)
    
    async def search_logs(self, search_request: LogSearchRequest) -> LogSearchResponse:
        """로그 검색 유스케이스"""
        return await self.log_service.search_logs(search_request)
    
    async def get_stats(self, days: int) -> LogStatsResponse:
        """로그 통계 조회 유스케이스"""
        return await self.log_service.get_stats(days)
    
    async def get_recent_logs(self, limit: int) -> LogSearchResponse:
        """최근 로그 조회 유스케이스"""
        return await self.log_service.get_recent_logs(limit)
