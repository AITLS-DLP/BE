"""Pydantic schemas for project management."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    name: str = Field(..., description="프로젝트 이름")
    description: Optional[str] = Field(None, description="프로젝트 설명")
    owner: Optional[str] = Field(None, description="담당자")
    status: str = Field("ACTIVE", description="프로젝트 상태")


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, description="프로젝트 이름")
    description: Optional[str] = Field(None, description="프로젝트 설명")
    owner: Optional[str] = Field(None, description="담당자")
    status: Optional[str] = Field(None, description="프로젝트 상태")
    total_detections: Optional[int] = Field(None, ge=0, description="총 탐지 건수")
    blocked_count: Optional[int] = Field(None, ge=0, description="차단된 탐지 건수")


class ProjectRead(ProjectBase):
    id: int
    total_detections: int = 0
    blocked_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
