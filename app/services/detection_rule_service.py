from sqlalchemy.orm import Session
from typing import List, Optional
from app.repositories.detection_rule_repository import DetectionRuleRepository
from app.models.detection_rule import DetectionRule
from app.schemas.detection_rule import DetectionRuleUpdate

class DetectionRuleService:
    def __init__(self, db: Session):
        self.repository = DetectionRuleRepository(db)

    def get_all_rules(self) -> List[DetectionRule]:
        return self.repository.get_all_rules()

    def update_rule_status(self, rule_id: int, is_active: bool) -> Optional[DetectionRule]:
        update_schema = DetectionRuleUpdate(is_active=is_active)
        return self.repository.update_rule(rule_id, update_schema)
