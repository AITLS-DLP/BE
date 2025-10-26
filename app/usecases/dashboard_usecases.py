"""Use cases for dashboard specific aggregations."""
from fastapi import Depends
import pytz

from app.services.log_service import LogService
from app.schemas.dashboard import DashboardSummaryResponse


class GetDashboardSummaryUseCase:
    """Fetch aggregated dashboard data for the admin UI."""

    def __init__(self, log_service: LogService = Depends()):
        self.log_service = log_service

    async def execute(self, days: int, tz: str, recent_limit: int) -> DashboardSummaryResponse:
        if tz not in pytz.all_timezones:
            raise ValueError(f"Invalid timezone: {tz}")
        return await self.log_service.get_dashboard_summary(days=days, tz=tz, recent_limit=recent_limit)
