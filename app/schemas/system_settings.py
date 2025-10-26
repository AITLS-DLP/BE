"""Schemas for global system settings."""
from typing import Optional

from pydantic import BaseModel, Field


class SystemSettingsResponse(BaseModel):
    default_timezone: str = Field(..., description="기본 시간대")
    data_retention_days: int = Field(..., ge=1, description="로그 보관 일수")
    maintenance_mode: bool = Field(..., description="시스템 점검 모드 여부")
    alert_email: Optional[str] = Field(None, description="알림 수신 이메일")


class SystemSettingsUpdate(BaseModel):
    default_timezone: Optional[str] = Field(None, description="기본 시간대")
    data_retention_days: Optional[int] = Field(None, ge=1, description="로그 보관 일수")
    maintenance_mode: Optional[bool] = Field(None, description="시스템 점검 모드 여부")
    alert_email: Optional[str] = Field(None, description="알림 수신 이메일")
