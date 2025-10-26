"""Business logic for detection feature settings."""
from typing import Dict

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.label_policy_repository import LabelPolicyRepository
from app.repositories.system_setting_repository import SystemSettingRepository
from app.schemas.detection_settings import (
    DetectionToggleResponse,
    DetectionToggleUpdate,
    LabelPolicyRead,
    LabelPolicyUpsert,
)


DETECTION_TOGGLE_KEYS = {
    "logging_enabled": True,
    "pseudonymize_enabled": False,
}


class DetectionSettingsService:
    """Coordinates label policies and detection toggles."""

    def __init__(self, db: AsyncSession):
        self.label_repository = LabelPolicyRepository(db)
        self.setting_repository = SystemSettingRepository(db)

    async def list_label_policies(self) -> list[LabelPolicyRead]:
        policies = await self.label_repository.list_policies()
        return [LabelPolicyRead.model_validate(policy) for policy in policies]

    async def upsert_label_policy(self, label: str, payload: LabelPolicyUpsert) -> LabelPolicyRead:
        policy = await self.label_repository.upsert(
            label=label,
            block=payload.block,
            updated_by=payload.updated_by,
        )
        return LabelPolicyRead.model_validate(policy)

    async def get_detection_toggles(self) -> DetectionToggleResponse:
        stored = await self.setting_repository.get_settings_map(DETECTION_TOGGLE_KEYS.keys())
        merged: Dict[str, bool] = {}
        for key, default in DETECTION_TOGGLE_KEYS.items():
            value = stored.get(key, default)
            if isinstance(value, bool):
                merged[key] = value
            elif isinstance(value, str):
                merged[key] = value.lower() in {"1", "true", "yes", "on"}
            else:
                merged[key] = bool(value)
        return DetectionToggleResponse(**merged)

    async def update_detection_toggles(self, payload: DetectionToggleUpdate) -> DetectionToggleResponse:
        changes = {}
        for key, value in payload.model_dump(exclude_unset=True).items():
            if key in DETECTION_TOGGLE_KEYS:
                changes[key] = bool(value)
        if changes:
            await self.setting_repository.upsert_settings(changes)
        return await self.get_detection_toggles()
