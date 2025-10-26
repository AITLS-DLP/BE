"""Dashboard summary schemas"""
from __future__ import annotations

from datetime import datetime
from typing import Dict, List

from pydantic import BaseModel, Field

from app.schemas.log import PIIDetectionLog


class DashboardOverview(BaseModel):
    """High level detection overview for the dashboard."""

    total_logs: int = Field(..., description="Total number of logs in the selected period")
    pii_detected_count: int = Field(..., description="Number of logs where PII was detected")
    pii_detection_rate: float = Field(..., description="Rate of PII detection in percentage")


class RealTimeStats(BaseModel):
    """Real time detection trend information."""

    hourly_counts: Dict[str, int] = Field(default_factory=dict, description="Hourly detection counts formatted to the requested timezone")
    total_last_hour: int = Field(0, description="Total detections in the most recent hour bucket")
    timezone: str = Field(..., description="Timezone applied to the hourly buckets")
    last_updated: datetime = Field(..., description="Timestamp when the summary was generated")


class QuarterlyStat(BaseModel):
    """Quarterly detection statistics."""

    label: str = Field(..., description="Quarter label (e.g. 2024-Q1)")
    total_count: int = Field(..., description="Total number of logs in the quarter")
    pii_detected_count: int = Field(..., description="Number of logs with PII detected in the quarter")


class DashboardSummaryResponse(BaseModel):
    """Aggregated dashboard data used by the admin UI."""

    overview: DashboardOverview
    real_time: RealTimeStats
    quarterly_stats: List[QuarterlyStat] = Field(default_factory=list)
    top_ips: List[Dict[str, int]] = Field(default_factory=list, description="Top client IPs")
    label_stats: Dict[str, int] = Field(default_factory=dict, description="Counts grouped by detected entity labels")
    label_action_breakdown: Dict[str, Dict[str, int]] = Field(default_factory=dict, description="Per label action counts (e.g. BLOCK/ALLOW)")
    log_status_stats: Dict[str, int] = Field(default_factory=dict, description="Counts grouped by metadata.log_status")
    project_stats: List[Dict[str, int]] = Field(default_factory=list, description="Counts grouped by metadata.project")
    detections: List[PIIDetectionLog] = Field(default_factory=list, description="Recent detection entries")
    ai_service_stats: Dict[str, int] = Field(default_factory=dict, description="Counts grouped by metadata.service")
    timezone: str = Field(..., description="Timezone requested by the client")
    range_days: int = Field(..., description="Number of days included in the summary window")
