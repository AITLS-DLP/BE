"""Schemas for detection feature settings."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class LabelPolicyBase(BaseModel):
    label: str = Field(..., description="탐지 라벨명")
    block: bool = Field(False, description="차단 여부")
    updated_by: Optional[str] = Field(None, description="최종 수정자")


class LabelPolicyRead(LabelPolicyBase):
    id: int
    updated_at: datetime

    class Config:
        orm_mode = True


class LabelPolicyUpsert(BaseModel):
    block: bool = Field(..., description="차단 여부")
    updated_by: Optional[str] = Field(None, description="최종 수정자")


class DetectionToggleResponse(BaseModel):
    logging_enabled: bool = Field(..., description="로그 저장 여부")
    pseudonymize_enabled: bool = Field(..., description="가명화 활성 여부")


class DetectionToggleUpdate(BaseModel):
    logging_enabled: Optional[bool] = Field(None, description="로그 저장 여부")
    pseudonymize_enabled: Optional[bool] = Field(None, description="가명화 활성 여부")
