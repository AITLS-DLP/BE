"""Label-based detection policy model."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from app.db.base import Base


class LabelPolicy(Base):
    """Configures block/allow behaviour per detected label."""

    __tablename__ = "label_policies"

    id = Column(Integer, primary_key=True, index=True)
    label = Column(String(255), unique=True, nullable=False, comment="탐지 라벨명")
    block = Column(Boolean, nullable=False, default=False, comment="차단 여부")
    updated_by = Column(String(255), nullable=True, comment="최종 수정자")
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
