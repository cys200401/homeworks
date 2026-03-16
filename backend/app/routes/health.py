from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.db import ping_database
from app.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    try:
        ping_database()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=503, detail=f"database unavailable: {exc}") from exc

    return HealthResponse(status="ok", database="ok")
