from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.admin import router as admin_router
from app.routes.health import router as health_router
from app.routes.traffic import router as traffic_router


def create_app() -> FastAPI:
    app = FastAPI(title="Daily Paper Admin API", version="0.1.0")

    cors_origins = [
        origin.strip()
        for origin in os.getenv("ADMIN_API_CORS_ORIGINS", "http://localhost:3000").split(",")
        if origin.strip()
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(admin_router)
    app.include_router(traffic_router)

    return app


app = create_app()
