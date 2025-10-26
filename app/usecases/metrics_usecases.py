"""
통계(Metrics) Use Cases
"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.log_service import LogService
import datetime
import pytz
from typing import Tuple

class GetTodayBlockCountUseCase:
    """오늘의 총 차단 횟수 조회 Use Case"""
    def __init__(self, db: AsyncSession = None):
        self.log_service = LogService()

    async def execute(self, tz: str) -> Tuple[int, datetime.datetime]:
        """
        Use Case 실행
        1. 지정된 시간대(tz) 기준 오늘 자정 시각 계산
        2. LogService를 통해 해당 시각 이후의 차단 로그 개수 조회
        """
        client_tz = pytz.timezone(tz)
        now_in_tz = datetime.datetime.now(client_tz)
        start_of_day_in_tz = now_in_tz.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # UTC로 변환하여 데이터베이스에 쿼리
        start_of_day_utc = start_of_day_in_tz.astimezone(pytz.utc)

        count = await self.log_service.get_block_count_since(start_of_day_utc)
        return count, start_of_day_in_tz
