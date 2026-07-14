from contextlib import asynccontextmanager
from typing import AsyncIterator

import structlog
from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware

from tsubo_api import __version__
from tsubo_api.config import get_settings
from tsubo_api.database import dispose_engine
from tsubo_api.errors import TsuboError, http_exception_handler, tsubo_error_handler
from tsubo_api.middleware import RequestIDMiddleware
from tsubo_api.routers import admin, coverage, fx, health, jurisdictions, listings, search, sources

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    logger.info("starting_api", app=settings.public_app_name, env=settings.app_env)
    yield
    await dispose_engine()
    logger.info("stopped_api")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=f"{settings.public_app_name} API",
        description="Tsubo platform API for akiya listings, coverage, and search.",
        version=__version__,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

    app.add_exception_handler(TsuboError, tsubo_error_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)

    app.include_router(health.router)
    app.include_router(listings.router, prefix="/api/v1")
    app.include_router(search.router, prefix="/api/v1")
    app.include_router(jurisdictions.router, prefix="/api/v1")
    app.include_router(sources.router, prefix="/api/v1")
    app.include_router(coverage.router, prefix="/api/v1")
    app.include_router(fx.router, prefix="/api/v1")
    app.include_router(admin.router, prefix="/api/v1")
    app.include_router(admin.prefecture_router, prefix="/api/v1")
    app.include_router(admin.municipality_router, prefix="/api/v1")

    return app


app = create_app()
