"""Repository for system settings."""
from typing import Any, Dict, Iterable, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.system_setting import SystemSetting


class SystemSettingRepository:
    """Manages persistence of key/value system settings."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_setting(self, key: str) -> Optional[SystemSetting]:
        result = await self.db.execute(select(SystemSetting).where(SystemSetting.key == key))
        return result.scalar_one_or_none()

    async def get_settings(self, keys: Optional[Iterable[str]] = None) -> List[SystemSetting]:
        stmt = select(SystemSetting)
        if keys is not None:
            stmt = stmt.where(SystemSetting.key.in_(list(keys)))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_settings_map(self, keys: Optional[Iterable[str]] = None) -> Dict[str, Any]:
        settings = await self.get_settings(keys)
        return {setting.key: setting.value for setting in settings}

    async def upsert_settings(self, values: Dict[str, Any]) -> List[SystemSetting]:
        stored: List[SystemSetting] = []
        for key, value in values.items():
            setting = await self.get_setting(key)
            if setting is None:
                setting = SystemSetting(key=key, value=value)
                self.db.add(setting)
            else:
                setting.value = value
            stored.append(setting)
        if not stored:
            return []
        await self.db.commit()
        for setting in stored:
            await self.db.refresh(setting)
        return stored
