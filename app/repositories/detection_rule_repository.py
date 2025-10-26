from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.detection_rule import DetectionRule
from app.schemas.detection_rule import DetectionRuleUpdate

class DetectionRuleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_rules(self) -> List[DetectionRule]:
        return self.db.query(DetectionRule).all()

    def get_rule_by_id(self, rule_id: int) -> Optional[DetectionRule]:
        return self.db.query(DetectionRule).filter(DetectionRule.id == rule_id).first()

    def update_rule(self, rule_id: int, update_data: DetectionRuleUpdate) -> Optional[DetectionRule]:
        rule = self.get_rule_by_id(rule_id)
        if rule:
            rule.is_active = update_data.is_active
            self.db.commit()
            self.db.refresh(rule)
        return rule
