"""Project domain model."""
from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.db.base import Base


class Project(Base):
    """Represents a customer project/workspace that groups detection activity."""

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, comment="프로젝트 이름")
    description = Column(Text, nullable=True, comment="프로젝트 설명")
    owner = Column(String(255), nullable=True, comment="프로젝트 담당자")
    status = Column(String(50), nullable=False, default="ACTIVE", comment="프로젝트 상태")
    total_detections = Column(Integer, nullable=False, default=0, comment="총 탐지 건수")
    blocked_count = Column(Integer, nullable=False, default=0, comment="차단된 탐지 건수")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
