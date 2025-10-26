"""Use cases for detection feature settings."""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.schemas.detection_settings import (
    DetectionToggleResponse,
    DetectionToggleUpdate,
    LabelPolicyRead,
    LabelPolicyUpsert,
)
from app.services.detection_settings_service import DetectionSettingsService


class DetectionSettingsUseCase:
    """Facade for detection settings operations."""

    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.service = DetectionSettingsService(db)

    async def list_label_policies(self) -> list[LabelPolicyRead]:
        return await self.service.list_label_policies()

    async def upsert_label_policy(self, label: str, payload: LabelPolicyUpsert) -> LabelPolicyRead:
        return await self.service.upsert_label_policy(label, payload)

    async def get_detection_toggles(self) -> DetectionToggleResponse:
        return await self.service.get_detection_toggles()

    async def update_detection_toggles(self, payload: DetectionToggleUpdate) -> DetectionToggleResponse:
        return await self.service.update_detection_toggles(payload)
