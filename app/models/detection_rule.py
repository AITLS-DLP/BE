from sqlalchemy import Column, Integer, String, Boolean, Text
from app.db.base import Base

class DetectionRule(Base):
    __tablename__ = "detection_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, comment="탐지 규칙 이름")
    description = Column(Text, nullable=True, comment="규칙에 대한 상세 설명")
    entity_type = Column(String, nullable=False, comment="탐지할 PII 엔티티 타입 (예: PERSON, PHONE)")
    is_active = Column(Boolean, default=True, nullable=False, comment="규칙 활성화 여부")
