from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.db import get_connection
from app.schemas import TrafficWriteRequest, TrafficWriteResponse

router = APIRouter(prefix="/api/traffic", tags=["traffic"])


def normalize_path(path: str) -> str:
    cleaned = path.strip() or "/"
    if not cleaned.startswith("/"):
        cleaned = f"/{cleaned}"
    return cleaned


@router.post("/pv", response_model=TrafficWriteResponse)
def record_page_view(payload: TrafficWriteRequest) -> TrafficWriteResponse:
    try:
        normalized_path = normalize_path(payload.path)

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    insert into traffic_daily_stats (
                      stat_date,
                      path,
                      page_type,
                      pv,
                      updated_at
                    )
                    values (current_date, %s, %s, 1, now())
                    on conflict (stat_date, path)
                    do update set
                      pv = traffic_daily_stats.pv + 1,
                      page_type = excluded.page_type,
                      updated_at = now()
                    """,
                    (normalized_path, payload.pageType),
                )
                connection.commit()

        return TrafficWriteResponse(ok=True)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc
