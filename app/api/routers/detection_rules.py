from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.usecases.detection_rule_usecases import DetectionRuleUseCase
from app.schemas.detection_rule import DetectionRuleRead, DetectionRuleUpdate

router = APIRouter()

@router.get("/", response_model=List[DetectionRuleRead], summary="탐지 규칙 목록 조회")
def get_all_rules(usecase: DetectionRuleUseCase = Depends()):
    """모든 AI 탐지 규칙의 목록을 조회합니다."""
    return usecase.get_all_rules()

@router.patch("/{rule_id}", response_model=DetectionRuleRead, summary="탐지 규칙 활성 상태 수정")
def update_rule_status(rule_id: int, rule_update: DetectionRuleUpdate, usecase: DetectionRuleUseCase = Depends()):
    """특정 탐지 규칙의 활성화(is_active) 상태를 수정합니다."""
    updated_rule = usecase.update_rule_status(rule_id, rule_update.is_active)
    if not updated_rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
    return updated_rule
