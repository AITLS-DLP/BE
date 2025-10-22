from typing import Any, Dict, List
from app.ai.model_manager import get_pii_detector
from app.schemas.pii import PIIDetectionResponse, DetectedEntity

class PIIDetectionService:
    """PII 탐지 비즈니스 로직을 처리하는 서비스"""

    def __init__(self):
        pass  # detector는 필요할 때 get_pii_detector()로 획득

    async def analyze_text(self, text: str) -> PIIDetectionResponse:
        """텍스트에서 개인정보를 탐지하고 결과를 반환"""
        if not isinstance(text, str) or not text.strip():
            raise ValueError("text must be a non-empty string")

        detector = get_pii_detector()
        if detector is None:
            raise RuntimeError("PII detector is not initialized.")

        try:
            # PII 탐지 수행 (단 한 번)
            detection_result: Dict[str, Any] = await detector.detect_pii(text)
        except Exception:
            # 필요 시 로깅/예외 변환
            raise

        # 안전 접근(get) 사용: 키 누락/형식 차이 방지
        has_pii: bool = bool(detection_result.get("has_pii", False))
        raw_entities: List[Dict[str, Any]] = detection_result.get("entities", [])
        entities: List[DetectedEntity] = [
            DetectedEntity(
                type=e.get("type", "UNKNOWN"),
                value=e.get("value", ""),
                confidence=float(e.get("confidence", 0.0)),
                token_count=int(e.get("token_count", 0)),
            )
            for e in raw_entities
        ]

        reason = self._generate_reason(has_pii, entities)
        details = self._generate_details(has_pii, entities)

        return PIIDetectionResponse(
            has_pii=has_pii,
            reason=reason,
            details=details,
            entities=entities,
        )

    def _generate_reason(self, has_pii: bool, entities: List[DetectedEntity]) -> str:
        """탐지 결과에 대한 이유 생성"""
        if not has_pii:
            return "개인정보가 탐지되지 않았습니다"
        if len(entities) == 1:
            return f"개인정보 1개 탐지됨 ({entities[0].type})"
        type_str = ", ".join(sorted({e.type for e in entities}))
        return f"개인정보 {len(entities)}개 탐지됨 ({type_str})"

    def _generate_details(self, has_pii: bool, entities: List[DetectedEntity]) -> str:
        """탐지된 개인정보에 대한 상세 설명 생성"""
        if not has_pii:
            return "입력된 텍스트에서 개인정보가 발견되지 않았습니다."
        parts = []
        for e in entities:
            parts.append(f"{e.type} '{e.value}' (신뢰도: {e.confidence:.1%})")
        return "다음 개인정보가 탐지되었습니다: " + ", ".join(parts)
