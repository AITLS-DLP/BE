from functools import lru_cache
from typing import Optional
import logging

from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import torch

from app.core.config import settings

logger = logging.getLogger(__name__)

# 전역 모델 인스턴스 저장소
_pii_detector_instance: Optional['PIIDetector'] = None

class PIIDetector:
    """PII 탐지 모델을 관리하는 클래스"""
    def __init__(self):
        self.model_name = settings.PII_MODEL_NAME
        self.default_threshold = settings.DEFAULT_PII_THRESHOLD
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        self._load_model()

    def _load_model(self):
        logger.info(f"Attempting to load tokenizer for {self.model_name}...")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            logger.info("Tokenizer loaded successfully.")

            logger.info(f"Attempting to load model for {self.model_name}...")
            self.model = AutoModelForTokenClassification.from_pretrained(self.model_name)
            logger.info("Model loaded successfully.")

            self.pipeline = pipeline(
                "ner",
                model=self.model,
                tokenizer=self.tokenizer,
                aggregation_strategy="simple",
                device=0 if torch.cuda.is_available() else -1,
            )
            logger.info("PII detection pipeline initialized.")
        except Exception as e:
            logger.error(f"Failed to load PII detection model: {e}", exc_info=True)
            raise RuntimeError(f"Failed to load PII detection model: {e}")

    async def detect_pii(self, text: str):
        """실제 PII 탐지 로직 (파이프라인 사용)"""
        if self.pipeline is None:
            raise RuntimeError("PII detection pipeline is not initialized.")
        # 실제 탐지 로직은 여기에 구현
        # 현재는 임시로 더미 결과 반환
        return {"has_pii": False, "entities": []}

@lru_cache(maxsize=1)
def get_pii_detector() -> PIIDetector:
    """
    PII 탐지 모델을 싱글톤으로 관리
    """
    global _pii_detector_instance
    
    if _pii_detector_instance is None:
        logger.info("Loading PII detection model (singleton initialization)...")
        try:
            _pii_detector_instance = PIIDetector()
            logger.info("PII detection model loaded successfully")
        except RuntimeError as e:
            logger.error(f"Failed to initialize PIIDetector: {e}")
            _pii_detector_instance = None # Ensure global is None if init fails
            raise # Re-raise the error
    logger.info(f"DEBUG: get_pii_detector returning instance: {_pii_detector_instance}") # DEBUG PRINT
    return _pii_detector_instance

def preload_models():
    """
    앱 시작 시 모델을 미리 로딩
    FastAPI startup event에서 호출
    """
    logger.info("Preloading AI models...")

    try:
        # PII 탐지 모델 로딩
        get_pii_detector()
        logger.info("✓ PII detection model loaded")

        logger.info("All AI models preloaded successfully")

    except Exception as e:
        logger.error(f"Failed to preload models: {e}")
        # 모델 로딩 실패 시에도 서버는 시작하되, 런타임에 에러 발생하도록 함
        raise

def cleanup_models():
    """
    앱 종료 시 모델 메모리 정리
    FastAPI shutdown event에서 호출
    """
    global _pii_detector_instance

    logger.info("Cleaning up AI models...")

    # PII 모델 정리
    if _pii_detector_instance is not None:
        if hasattr(_pii_detector_instance, 'model') and hasattr(_pii_detector_instance.model, 'cpu'):
            _pii_detector_instance.model.cpu()
        _pii_detector_instance = None
        get_pii_detector.cache_clear()
        logger.info("✓ PII detection model cleaned up")

    logger.info("All AI models cleaned up")
