from fastapi import APIRouter, HTTPException, status, Query, Depends
from fastapi.responses import JSONResponse
from typing import Optional, List
from datetime import datetime, timedelta
from app.schemas.log import LogSearchRequest, LogSearchResponse, LogStatsResponse, LogLevel
from app.services.log_service import LogService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# 서비스 인스턴스 생성
log_service = LogService()

@router.get("/search",
            response_model=LogSearchResponse,
            summary="로그 검색",
            description="PII 탐지 로그를 검색합니다. 다양한 필터 조건을 지원합니다.")
async def search_logs(
    # 시간 범위
    start_time: Optional[datetime] = Query(None, description="검색 시작 시간 (ISO 8601 형식)"),
    end_time: Optional[datetime] = Query(None, description="검색 종료 시간 (ISO 8601 형식)"),
    
    # 필터 조건
    client_ip: Optional[str] = Query(None, description="클라이언트 IP 주소"),
    has_pii: Optional[bool] = Query(None, description="PII 탐지 여부 (true/false)"),
    entity_types: Optional[str] = Query(None, description="엔티티 타입 (쉼표로 구분, 예: PERSON,PHONE)"),
    level: Optional[LogLevel] = Query(None, description="로그 레벨"),
    
    # 검색 조건
    search_text: Optional[str] = Query(None, description="텍스트 검색 (입력 텍스트에서 검색)"),
    
    # 페이징
    page: int = Query(1, description="페이지 번호", ge=1),
    size: int = Query(20, description="페이지 크기", ge=1, le=100)
) -> LogSearchResponse:
    """
    PII 탐지 로그 검색 API
    
    다양한 필터 조건으로 로그를 검색할 수 있습니다:
    
    - **시간 범위**: start_time, end_time으로 특정 기간 필터
    - **IP 필터**: client_ip로 특정 클라이언트의 요청만 조회
    - **PII 탐지 여부**: has_pii로 개인정보가 탐지된/안된 요청 구분
    - **엔티티 타입**: entity_types로 특정 타입의 개인정보만 조회
    - **텍스트 검색**: search_text로 입력 텍스트 내용 검색
    
    반환값:
    - **logs**: 검색된 로그 목록
    - **total**: 전체 로그 개수
    - **page**: 현재 페이지
    - **stats**: 통계 정보
    """
    try:
        # 엔티티 타입 파싱
        entity_types_list = None
        if entity_types:
            entity_types_list = [t.strip() for t in entity_types.split(",") if t.strip()]
        
        # 검색 요청 객체 생성
        search_request = LogSearchRequest(
            start_time=start_time,
            end_time=end_time,
            client_ip=client_ip,
            has_pii=has_pii,
            entity_types=entity_types_list,
            level=level,
            search_text=search_text,
            page=page,
            size=size
        )
        
        # 로그 검색 수행
        result = await log_service.search_logs(search_request)
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to search logs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="로그 검색 중 오류가 발생했습니다."
        )

@router.get("/stats",
            response_model=LogStatsResponse,
            summary="로그 통계",
            description="PII 탐지 로그의 통계 정보를 조회합니다.")
async def get_log_stats(
    days: int = Query(7, description="통계 조회 기간 (일 단위)", ge=1, le=365)
) -> LogStatsResponse:
    """
    로그 통계 조회 API
    
    지정된 기간 동안의 로그 통계를 제공합니다:
    
    - **전체 로그 개수**: 지정 기간의 총 로그 수
    - **PII 탐지 통계**: 개인정보가 탐지된 로그 수와 탐지율
    - **엔티티 타입별 통계**: 탐지된 개인정보 타입별 개수
    - **시간별 통계**: 시간대별 로그 발생 현황
    - **상위 IP 통계**: 가장 많은 요청을 보낸 IP 주소들
    - **평균 처리 시간**: PII 탐지 평균 소요 시간
    """
    try:
        stats = await log_service.get_stats(days)
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get log stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="로그 통계 조회 중 오류가 발생했습니다."
        )

@router.get("/recent",
            response_model=LogSearchResponse,
            summary="최근 로그",
            description="최근 24시간의 PII 탐지 로그를 조회합니다.")
async def get_recent_logs(
    limit: int = Query(50, description="조회할 로그 개수", ge=1, le=200)
) -> LogSearchResponse:
    """
    최근 로그 조회 API
    
    최근 24시간 동안의 PII 탐지 로그를 최신순으로 조회합니다.
    
    반환값:
    - **logs**: 최근 로그 목록 (최신순)
    - **total**: 전체 로그 개수
    - **stats**: 간단한 통계 정보
    """
    try:
        result = await log_service.get_recent_logs(limit)
        return result
        
    except Exception as e:
        logger.error(f"Failed to get recent logs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="최근 로그 조회 중 오류가 발생했습니다."
        )

@router.get("/health",
            summary="로그 서비스 상태 확인",
            description="로그 서비스와 Elasticsearch 연결 상태를 확인합니다.")
async def health_check():
    """로그 서비스 헬스체크"""
    try:
        # 간단한 검색으로 연결 상태 확인
        search_request = LogSearchRequest(
            start_time=datetime.now() - timedelta(minutes=1),
            end_time=datetime.now(),
            page=1,
            size=1
        )
        
        result = await log_service.search_logs(search_request)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "healthy",
                "message": "Log service is running",
                "elasticsearch_connected": True,
                "total_logs": result.total
            }
        )
        
    except Exception as e:
        logger.error(f"Log service health check failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "message": "Log service is not available",
                "elasticsearch_connected": False,
                "error": str(e)
            }
        )
