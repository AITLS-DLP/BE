"""
통계(Metrics) 관련 스키마
"""
from pydantic import BaseModel
from datetime import datetime

class TodayBlockCountResponse(BaseModel):
    """오늘의 총 차단 횟수 응답 스키마"""
    count: int
    start_of_day: str
    timezone: str

    class Config:
        from_attributes = True
