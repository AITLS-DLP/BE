import os
from pydantic import BaseModel

class Settings(BaseModel):
    # 데이터베이스 설정 (향후 사용 예정)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://admin:password123@localhost:5432/ai_tlsdlp"
    )

    # AI 모델 설정
    PII_MODEL_NAME: str = os.getenv("PII_MODEL_NAME", "psh3333/roberta-large-korean-pii5")

    # 분석 설정
    DEFAULT_PII_THRESHOLD: float = float(os.getenv("DEFAULT_PII_THRESHOLD", "0.59"))

    # 모델 모드
    MODEL_MODE: str = os.getenv("MODEL_MODE", "LOCAL")  # LOCAL | REMOTE

settings = Settings()