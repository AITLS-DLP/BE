from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class LogLevel(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    DEBUG = "DEBUG"

class PIIDetectionLog(BaseModel):
    """PII 탐지 로그 스키마"""
    
    # 기본 정보
    id: Optional[str] = Field(None, description="로그 고유 ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="로그 생성 시간")
    level: LogLevel = Field(LogLevel.INFO, description="로그 레벨")
    
    # 요청 정보
    client_ip: str = Field(..., description="클라이언트 IP 주소")
    user_agent: Optional[str] = Field(None, description="사용자 에이전트")
    request_id: Optional[str] = Field(None, description="요청 고유 ID")
    
    # PII 탐지 결과
    input_text: str = Field(..., description="입력된 텍스트")
    text_length: int = Field(..., description="입력 텍스트 길이")
    has_pii: bool = Field(..., description="PII 탐지 여부")
    
    # 탐지된 엔티티 정보
    detected_entities: List[Dict[str, Any]] = Field(default_factory=list, description="탐지된 PII 엔티티들")
    entity_count: int = Field(0, description="탐지된 엔티티 개수")
    entity_types: List[str] = Field(default_factory=list, description="탐지된 엔티티 타입들")
    
    # 처리 정보
    processing_time_ms: Optional[float] = Field(None, description="처리 시간 (밀리초)")
    model_confidence: Optional[float] = Field(None, description="모델 전체 신뢰도")
    
    # 응답 정보
    reason: Optional[str] = Field(None, description="탐지 결과 이유")
    details: Optional[str] = Field(None, description="상세 설명")
    
    # 추가 메타데이터
    metadata: Dict[str, Any] = Field(default_factory=dict, description="추가 메타데이터")

class LogSearchRequest(BaseModel):
    """로그 검색 요청 스키마"""
    
    # 시간 범위
    start_time: Optional[datetime] = Field(None, description="검색 시작 시간")
    end_time: Optional[datetime] = Field(None, description="검색 종료 시간")
    
    # 필터 조건
    client_ip: Optional[str] = Field(None, description="클라이언트 IP 필터")
    has_pii: Optional[bool] = Field(None, description="PII 탐지 여부 필터")
    entity_types: Optional[List[str]] = Field(None, description="엔티티 타입 필터")
    level: Optional[LogLevel] = Field(None, description="로그 레벨 필터")
    
    # 검색 조건
    search_text: Optional[str] = Field(None, description="텍스트 검색 (입력 텍스트에서)")
    
    # 페이징
    page: int = Field(1, description="페이지 번호", ge=1)
    size: int = Field(20, description="페이지 크기", ge=1, le=100)

class LogSearchResponse(BaseModel):
    """로그 검색 응답 스키마"""
    
    logs: List[PIIDetectionLog] = Field(..., description="검색된 로그 목록")
    total: int = Field(..., description="전체 로그 개수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")
    total_pages: int = Field(..., description="전체 페이지 수")
    
    # 통계 정보
    stats: Dict[str, Any] = Field(default_factory=dict, description="통계 정보")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "logs": [
                        {
                            "id": "log_123",
                            "timestamp": "2024-01-15T10:30:00Z",
                            "client_ip": "192.168.1.100",
                            "has_pii": True,
                            "entity_types": ["PERSON", "PHONE"],
                            "processing_time_ms": 250.5
                        }
                    ],
                    "total": 150,
                    "page": 1,
                    "size": 20,
                    "total_pages": 8,
                    "stats": {
                        "total_pii_detected": 45,
                        "avg_processing_time": 180.2
                    }
                }
            ]
        }
    }

class LogStatsResponse(BaseModel):
    """로그 통계 응답 스키마"""
    
    total_logs: int = Field(..., description="전체 로그 개수")
    pii_detected_count: int = Field(..., description="PII 탐지된 로그 개수")
    pii_detection_rate: float = Field(..., description="PII 탐지율")
    
    # 엔티티 타입별 통계
    entity_type_stats: Dict[str, int] = Field(default_factory=dict, description="엔티티 타입별 개수")
    
    # 시간별 통계
    hourly_stats: Dict[str, int] = Field(default_factory=dict, description="시간별 로그 개수")
    
    # 평균 처리 시간
    avg_processing_time: float = Field(..., description="평균 처리 시간 (밀리초)")
    
    # IP별 통계 (상위 10개)
    top_ips: List[Dict[str, Any]] = Field(default_factory=list, description="상위 IP 주소들")
