from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.db import get_connection, ping_database
from app.schemas import (
    HealthResponse,
    OverviewResponse,
    OverviewStageItem,
    PipelineRunItem,
    PipelineRunsResponse,
    RunErrorItem,
    RunErrorsResponse,
    TrafficDailyItem,
)

router = APIRouter(prefix="/api/admin", tags=["admin"])


def build_health() -> HealthResponse:
    ping_database()
    return HealthResponse(status="ok", database="ok")


@router.get("/overview", response_model=OverviewResponse)
def overview() -> OverviewResponse:
    try:
        health = build_health()
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    select distinct on (stage)
                      stage,
                      status,
                      started_at,
                      finished_at
                    from pipeline_runs
                    order by stage, started_at desc
                    """
                )
                latest_stages = [
                    OverviewStageItem(
                        stage=row["stage"],
                        status=row["status"],
                        startedAt=row["started_at"],
                        finishedAt=row["finished_at"],
                    )
                    for row in cursor.fetchall()
                ]

                cursor.execute(
                    """
                    select count(*) as count
                    from run_errors
                    where created_at >= now() - interval '7 days'
                    """
                )
                error_row = cursor.fetchone()
                recent_error_count = int(error_row["count"]) if error_row else 0

                cursor.execute(
                    """
                    select stat_date, coalesce(sum(pv), 0) as total_pv
                    from traffic_daily_stats
                    where stat_date >= current_date - interval '6 days'
                    group by stat_date
                    order by stat_date desc
                    """
                )
                recent_pv = [
                    TrafficDailyItem(
                        statDate=row["stat_date"],
                        totalPv=int(row["total_pv"]),
                    )
                    for row in cursor.fetchall()
                ]

        return OverviewResponse(
            health=health,
            latestStages=latest_stages,
            recentErrorCount=recent_error_count,
            recentPv=recent_pv,
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/pipeline-runs", response_model=PipelineRunsResponse)
def pipeline_runs(limit: int = Query(default=20, ge=1, le=100)) -> PipelineRunsResponse:
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    select
                      id::text as id,
                      run_date,
                      stage,
                      status,
                      success_count,
                      failed_count,
                      skipped_count,
                      started_at,
                      finished_at,
                      duration_ms,
                      notes,
                      params_json
                    from pipeline_runs
                    order by started_at desc
                    limit %s
                    """,
                    (limit,),
                )
                items = [
                    PipelineRunItem(
                        id=row["id"],
                        runDate=row["run_date"],
                        stage=row["stage"],
                        status=row["status"],
                        successCount=row["success_count"],
                        failedCount=row["failed_count"],
                        skippedCount=row["skipped_count"],
                        startedAt=row["started_at"],
                        finishedAt=row["finished_at"],
                        durationMs=row["duration_ms"],
                        notes=row["notes"],
                        params=row["params_json"],
                    )
                    for row in cursor.fetchall()
                ]

        return PipelineRunsResponse(items=items)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/errors", response_model=RunErrorsResponse)
def errors(limit: int = Query(default=50, ge=1, le=100)) -> RunErrorsResponse:
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    select
                      id::text as id,
                      pipeline_run_id::text as pipeline_run_id,
                      stage,
                      error_code,
                      error_message,
                      paper_arxiv_id,
                      created_at
                    from run_errors
                    order by created_at desc
                    limit %s
                    """,
                    (limit,),
                )
                items = [
                    RunErrorItem(
                        id=row["id"],
                        pipelineRunId=row["pipeline_run_id"],
                        stage=row["stage"],
                        errorCode=row["error_code"],
                        errorMessage=row["error_message"],
                        paperArxivId=row["paper_arxiv_id"],
                        createdAt=row["created_at"],
                    )
                    for row in cursor.fetchall()
                ]

        return RunErrorsResponse(items=items)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc
