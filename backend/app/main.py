from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from .routes.auth import router as auth_router
from .routes.acme import router as acme_router
from .routes.directory import router as directory_router
from .routes.members import router as members_router
from .routes.providers import router as providers_router
from .routes.reports import router as reports_router
from .routes.service_records import router as service_records_router
from .routes.services import router as services_router
from .settings import settings


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth_router)
    app.include_router(acme_router)
    app.include_router(directory_router)
    app.include_router(members_router)
    app.include_router(providers_router)
    app.include_router(services_router)
    app.include_router(service_records_router)
    app.include_router(reports_router)

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
init_db()

