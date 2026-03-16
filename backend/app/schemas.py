from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    database: str


class PipelineRunItem(BaseModel):
    id: str
    runDate: date
    stage: str
    status: str
    successCount: int
    failedCount: int
    skippedCount: int
    startedAt: datetime
    finishedAt: datetime | None
    durationMs: int | None
    notes: str | None
    params: dict[str, Any] | None


class RunErrorItem(BaseModel):
    id: str
    pipelineRunId: str | None
    stage: str
    errorCode: str | None
    errorMessage: str
    paperArxivId: str | None
    createdAt: datetime


class TrafficDailyItem(BaseModel):
    statDate: date
    totalPv: int


class OverviewStageItem(BaseModel):
    stage: str
    status: str
    startedAt: datetime
    finishedAt: datetime | None


class OverviewResponse(BaseModel):
    health: HealthResponse
    latestStages: list[OverviewStageItem]
    recentErrorCount: int
    recentPv: list[TrafficDailyItem]


class PipelineRunsResponse(BaseModel):
    items: list[PipelineRunItem]


class RunErrorsResponse(BaseModel):
    items: list[RunErrorItem]


class TrafficWriteRequest(BaseModel):
    path: str
    pageType: Literal["home", "daily"]


class TrafficWriteResponse(BaseModel):
    ok: bool
