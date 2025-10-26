"""System-wide configuration model."""
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON

from app.db.base import Base


class SystemSetting(Base):
    """Stores key/value configuration for the platform."""

    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), unique=True, nullable=False, comment="설정 키")
    value = Column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        comment="설정 값(JSON)",
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
