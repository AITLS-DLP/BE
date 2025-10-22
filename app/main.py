# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers.pii import router as pii_router
from app.api.routers.auth import router as auth_router
from app.api.routers.logs import router as logs_router
from app.api.routers.detection_rules import router as detection_rules_router
from app.api.routers import metrics as metrics_router
from app.ai.model_manager import preload_models, cleanup_models
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI-TLS-DLP Backend",
    description="AI 기반 개인정보 탐지 API (인증 필수)",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 미들웨어 추가 (개발환경용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 추가
app.include_router(auth_router, tags=["Authentication"])  # 인증 API (인증 불필요)
app.include_router(pii_router, prefix="/api/v1/pii", tags=["PII Detection"])  # PII API (인증 필수)
app.include_router(logs_router, prefix="/api/v1/logs", tags=["Logs"])  # 로그 API
app.include_router(detection_rules_router, prefix="/api/v1/detection-rules", tags=["Detection Rules"])  # 탐지 규칙 API
app.include_router(metrics_router.router) # 통계 API

# 애플리케이션 시작/종료 이벤트 핸들러
@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행"""
    logger.info("Starting AI-TLS-DLP Backend...")
    preload_models()  # 모델 사전 로딩
    logger.info("AI-TLS-DLP Backend startup completed")

@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 실행"""
    logger.info("Shutting down AI-TLS-DLP Backend...")
    cleanup_models()  # 모델 메모리 정리
    logger.info("AI-TLS-DLP Backend shutdown completed")

@app.get("/", summary="API 상태 확인")
async def root():
    """루트 엔드포인트 - API 상태 확인"""
    return {
        "message": "AI-TLS-DLP Backend API is running",
        "description": "PII Detection API with Authentication",
        "status": "ok",
        "version": "1.1.0",
        "features": [
            "JWT Authentication",
            "User Registration & Login",
            "Korean PII Detection (RoBERTa + Regex)"
        ],
        "endpoints": {
            "docs": "/docs",
            "register": "/api/v1/auth/register",
            "login": "/api/v1/auth/login",
            "me": "/api/v1/auth/me",
            "detect": "/api/v1/pii/detect",
            "health": "/api/v1/pii/health"
        },
        "note": "PII API requires JWT authentication (Bearer token)"
    }