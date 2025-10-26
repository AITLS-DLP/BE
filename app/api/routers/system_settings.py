"""System settings API."""
from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.system_settings import SystemSettingsResponse, SystemSettingsUpdate
from app.usecases.system_settings_usecases import SystemSettingsUseCase

router = APIRouter(prefix="/api/v1/system-settings", tags=["System Settings"])


@router.get("/", response_model=SystemSettingsResponse, summary="시스템 설정 조회")
async def get_system_settings(usecase: SystemSettingsUseCase = Depends()) -> SystemSettingsResponse:
    return await usecase.get_settings()


@router.patch("/", response_model=SystemSettingsResponse, summary="시스템 설정 수정")
async def update_system_settings(
    payload: SystemSettingsUpdate,
    usecase: SystemSettingsUseCase = Depends(),
) -> SystemSettingsResponse:
    try:
        return await usecase.update_settings(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
