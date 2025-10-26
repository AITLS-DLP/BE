"""Detection feature settings API."""
from fastapi import APIRouter, Depends, status
from typing import List

from app.schemas.detection_settings import (
    DetectionToggleResponse,
    DetectionToggleUpdate,
    LabelPolicyRead,
    LabelPolicyUpsert,
)
from app.usecases.detection_settings_usecases import DetectionSettingsUseCase

router = APIRouter(prefix="/api/v1/detection-settings", tags=["Detection Settings"])


@router.get("/labels", response_model=List[LabelPolicyRead], summary="라벨 정책 목록")
async def list_label_policies(usecase: DetectionSettingsUseCase = Depends()) -> List[LabelPolicyRead]:
    return await usecase.list_label_policies()


@router.put("/labels/{label}", response_model=LabelPolicyRead, summary="라벨 정책 생성/수정")
async def upsert_label_policy(
    label: str,
    payload: LabelPolicyUpsert,
    usecase: DetectionSettingsUseCase = Depends(),
) -> LabelPolicyRead:
    return await usecase.upsert_label_policy(label, payload)


@router.get("/toggles", response_model=DetectionToggleResponse, summary="탐지 기능 토글 조회")
async def get_detection_toggles(usecase: DetectionSettingsUseCase = Depends()) -> DetectionToggleResponse:
    return await usecase.get_detection_toggles()


@router.patch("/toggles", response_model=DetectionToggleResponse, summary="탐지 기능 토글 수정")
async def update_detection_toggles(
    payload: DetectionToggleUpdate,
    usecase: DetectionSettingsUseCase = Depends(),
) -> DetectionToggleResponse:
    return await usecase.update_detection_toggles(payload)
