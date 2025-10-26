from pydantic import BaseModel
from typing import Optional

class DetectionRuleBase(BaseModel):
    name: str
    description: Optional[str] = None
    entity_type: str
    is_active: bool = True

class DetectionRuleRead(DetectionRuleBase):
    id: int

    class Config:
        orm_mode = True

class DetectionRuleUpdate(BaseModel):
    is_active: bool
