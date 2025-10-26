"""Dashboard aggregation endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.schemas.dashboard import DashboardSummaryResponse
from app.usecases.dashboard_usecases import GetDashboardSummaryUseCase

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard"])


@router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="대시보드 요약 데이터",
    description="관리자 대시보드 위젯에 필요한 통계를 한 번에 제공합니다.",
)
async def get_dashboard_summary(
    usecase: GetDashboardSummaryUseCase = Depends(),
    days: int = Query(90, ge=1, le=365, description="Summary window in days"),
    tz: str = Query("UTC", description="Timezone for aggregations"),
    recent_limit: int = Query(10, ge=1, le=100, description="Number of recent detection logs to return"),
) -> DashboardSummaryResponse:
    try:
        return await usecase.execute(days=days, tz=tz, recent_limit=recent_limit)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load dashboard summary",
        ) from exc
