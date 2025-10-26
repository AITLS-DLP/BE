"""Use cases for system settings."""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.schemas.system_settings import SystemSettingsResponse, SystemSettingsUpdate
from app.services.system_settings_service import SystemSettingsService


class SystemSettingsUseCase:
    """Expose system setting operations."""

    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.service = SystemSettingsService(db)

    async def get_settings(self) -> SystemSettingsResponse:
        return await self.service.get_settings()

    async def update_settings(self, payload: SystemSettingsUpdate) -> SystemSettingsResponse:
        return await self.service.update_settings(payload)
