"""
통계(Metrics) API (Presentation Layer)
"""
from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import pytz # pytz import 추가

from app.db.session import get_db
from app.schemas.metrics import TodayBlockCountResponse
from app.usecases.metrics_usecases import GetTodayBlockCountUseCase

router = APIRouter(prefix="/api/v1/metrics", tags=["Metrics"])


@router.get("/blocks/today", response_model=TodayBlockCountResponse, status_code=status.HTTP_200_OK)
async def get_today_block_count(
    db: AsyncSession = Depends(get_db),
    tz: str = Query("UTC", description="클라이언트의 시간대 (예: Asia/Seoul)")
):
    """
    오늘의 총 차단 횟수를 조회합니다.
    지정된 시간대(tz) 기준 00:00부터 현재까지의 차단 횟수를 집계합니다.
    """
    try:
        # 유효한 시간대인지 확인
        if tz not in pytz.all_timezones:
            raise HTTPException(status_code=400, detail=f"Invalid timezone: {tz}")

        use_case = GetTodayBlockCountUseCase(db)
        count, start_of_day = await use_case.execute(tz=tz) # tz 전달
        
        return TodayBlockCountResponse(
            count=count,
            start_of_day=start_of_day.isoformat(),
            timezone=tz
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {e}"
        )
