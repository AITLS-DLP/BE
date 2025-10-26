"""Business logic for global system settings."""
from typing import Any, Dict

import pytz
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.system_setting_repository import SystemSettingRepository
from app.schemas.system_settings import SystemSettingsResponse, SystemSettingsUpdate


DEFAULT_SYSTEM_SETTINGS: Dict[str, Any] = {
    "default_timezone": "UTC",
    "data_retention_days": 90,
    "maintenance_mode": False,
    "alert_email": None,
}


class SystemSettingsService:
    """Handles retrieval and updates of system-wide configuration."""

    def __init__(self, db: AsyncSession):
        self.repository = SystemSettingRepository(db)

    async def get_settings(self) -> SystemSettingsResponse:
        stored = await self.repository.get_settings_map(DEFAULT_SYSTEM_SETTINGS.keys())
        values: Dict[str, Any] = {}
        for key, default in DEFAULT_SYSTEM_SETTINGS.items():
            value = stored.get(key, default)
            if key == "data_retention_days" and value is not None:
                try:
                    value = int(value)
                except (TypeError, ValueError):
                    value = default
            elif key == "maintenance_mode":
                value = bool(value)
            elif key == "default_timezone" and value is None:
                value = default
            values[key] = value
        return SystemSettingsResponse(**values)

    async def update_settings(self, payload: SystemSettingsUpdate) -> SystemSettingsResponse:
        changes = payload.model_dump(exclude_unset=True)
        if changes:
            if "default_timezone" in changes:
                timezone = changes["default_timezone"]
                if timezone not in pytz.all_timezones:
                    raise ValueError(f"Invalid timezone: {timezone}")
            if "data_retention_days" in changes:
                changes["data_retention_days"] = int(changes["data_retention_days"])
            await self.repository.upsert_settings(changes)
        return await self.get_settings()
