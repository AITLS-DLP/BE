from fastapi import Depends
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.dependencies import get_db
from app.services.detection_rule_service import DetectionRuleService
from app.models.detection_rule import DetectionRule

class DetectionRuleUseCase:
    def __init__(self, db: Session = Depends(get_db)):
        self.service = DetectionRuleService(db)

    def get_all_rules(self) -> List[DetectionRule]:
        return self.service.get_all_rules()

    def update_rule_status(self, rule_id: int, is_active: bool) -> Optional[DetectionRule]:
        return self.service.update_rule_status(rule_id, is_active)
