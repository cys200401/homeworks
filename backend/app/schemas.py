from __future__ import annotations

from datetime import date, datetime, time
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
    pageType: Literal["home", "daily", "workspace", "settings"]


class TrafficWriteResponse(BaseModel):
    ok: bool


class ThemePalette(BaseModel):
    background: str
    foreground: str
    accent: str
    accentSoft: str
    surface: str
    surfaceAlt: str
    border: str


class ThemeTokens(BaseModel):
    themeName: str
    fontPreset: Literal["editorial", "modern", "mono"]
    layoutDensity: Literal["airy", "balanced", "compact"]
    cardStyle: Literal["panel", "pill", "outline"]
    heroPattern: Literal["mesh", "rays", "grid"]
    borderRadius: Literal["sharp", "soft", "round"]
    motionLevel: Literal["calm", "lively"]
    palette: ThemePalette


class UserDeliveryProfilePayload(BaseModel):
    deliveryEnabled: bool
    deliveryLocalTime: time
    windowStartHour: int
    windowEndHour: int
    lookbackDays: int
    categories: list[str]
    nextRunAt: datetime | None
    lastRunAt: datetime | None


class UserSummaryItem(BaseModel):
    handle: str
    displayName: str
    timezone: str
    deliveryEnabled: bool
    deliveryLocalTime: time
    categories: list[str]
    themeName: str
    nextRunAt: datetime | None
    latestReportDate: date | None


class UserListResponse(BaseModel):
    items: list[UserSummaryItem]


class UserProfileResponse(BaseModel):
    handle: str
    displayName: str
    email: str | None
    timezone: str
    delivery: UserDeliveryProfilePayload
    themePrompt: str
    theme: ThemeTokens
    latestReportDate: date | None


class UpdateUserPreferencesRequest(BaseModel):
    displayName: str
    timezone: str
    deliveryEnabled: bool
    deliveryLocalTime: time
    windowStartHour: int
    windowEndHour: int
    lookbackDays: int
    categories: list[str]


class UpdateUserThemeRequest(BaseModel):
    promptText: str


class UserThemeResponse(BaseModel):
    promptText: str
    theme: ThemeTokens


class UserPaperBase(BaseModel):
    arxivId: str
    title: str
    authors: list[str]
    abstract: str
    categories: list[str]
    arxivUrl: str
    tldr: str


class UserPaperHighlight(UserPaperBase):
    problem: str
    methodology: str
    keyFindings: list[str]
    significance: str
    limitations: str | None = None


class UserPaperBrief(UserPaperBase):
    comment: str


class UserReportPayload(BaseModel):
    date: date
    title: str
    summary: str
    totalPapers: int
    tags: list[str]
    trends: str | None = None
    highlights: list[UserPaperHighlight]
    notables: list[UserPaperBrief]
    publishedAt: datetime
    theme: ThemeTokens
    source: dict[str, Any]


class UserWorkspaceResponse(BaseModel):
    user: UserProfileResponse
    report: UserReportPayload | None
