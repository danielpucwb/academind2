"""FastAPI application entrypoint."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import artefacts, courses, disciplines, health, merge, pages, upload
from app.core.config import SettingsModel, load_settings
from app.core.db import init_db, make_engine_from_settings
from app.logging_config import configure_logging

logger = logging.getLogger(__name__)
STATIC_DIR = Path(__file__).resolve().parent / "static"


def create_app(*, settings: SettingsModel | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        resolved = settings or load_settings()
        configure_logging(resolved)
        logger.info(
            "Boot acadeMIND | sqlite=%s | storage=%s",
            resolved.sqlite_path_abs,
            resolved.storage_root_abs,
        )
        engine = make_engine_from_settings(resolved.sqlite_path_abs)
        init_db(engine)
        app.state.settings = resolved
        app.state.engine = engine
        yield
        engine.dispose()

    app = FastAPI(title="acadeMIND", lifespan=lifespan)
    app.include_router(health.router)
    app.include_router(upload.router)
    app.include_router(merge.router)
    app.include_router(courses.router)
    app.include_router(disciplines.router)
    app.include_router(artefacts.router)
    app.include_router(pages.router)
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    return app


app = create_app()
