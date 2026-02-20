"""Main FastAPI application entry point."""

import asyncio
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from src.api.router import api_router
from src.api.public_site import router as public_site_router
from src.cache import init_cache, get_cache
from src.config import get_settings
from src.logging import get_logger, setup_logging
from src.middleware import RequestContextMiddleware


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        """Application lifespan events."""
        # Startup
        setup_logging()
        logger = get_logger("lifespan")
        logger.info("application_starting", environment=settings.environment)

        import os
        os.makedirs(settings.git_repos_path, exist_ok=True)

        # Initialize Redis cache
        cache = await init_cache()
        app.state.cache = cache
        if await cache.ping():
            logger.info("redis_connected")
        else:
            logger.warning("redis_unavailable")

        yield

        # Shutdown
        cache = get_cache()
        if cache:
            await cache.close()

        from src.db.session import engine
        await engine.dispose()
        logger.info("application_stopped")

    application = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
        openapi_url=f"{settings.api_prefix}/openapi.json",
        docs_url=f"{settings.api_prefix}/docs",
        redoc_url=f"{settings.api_prefix}/redoc",
        lifespan=lifespan,
    )

    # CORS middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request context middleware (correlation IDs, timing)
    application.add_middleware(RequestContextMiddleware)

    # Include API router
    application.include_router(api_router, prefix=settings.api_prefix)

    # Include public site router for published documentation
    application.include_router(public_site_router, prefix="/s")

    @application.get("/health")
    async def health_check() -> dict[str, Any]:
        """Comprehensive health check with dependency status."""
        checks: dict[str, str] = {}
        timeout = 2.0

        async def check_database() -> str:
            try:
                from src.db.session import async_session_maker
                async with async_session_maker() as session:
                    await session.execute(text("SELECT 1"))
                return "ok"
            except Exception:
                return "error"

        async def check_redis() -> str:
            try:
                cache = get_cache()
                if cache and await cache.ping():
                    return "ok"
                return "error"
            except Exception:
                return "error"

        async def check_meilisearch() -> str:
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    resp = await client.get(f"{settings.meilisearch_url}/health")
                    if resp.status_code == 200:
                        return "ok"
                    return "error"
            except Exception:
                return "error"

        db_result, redis_result, meili_result = await asyncio.gather(
            asyncio.wait_for(check_database(), timeout=timeout),
            asyncio.wait_for(check_redis(), timeout=timeout),
            asyncio.wait_for(check_meilisearch(), timeout=timeout),
            return_exceptions=True,
        )

        checks["database"] = db_result if isinstance(db_result, str) else "error"
        checks["redis"] = redis_result if isinstance(redis_result, str) else "error"
        checks["meilisearch"] = meili_result if isinstance(meili_result, str) else "error"

        all_ok = all(v == "ok" for v in checks.values())
        any_ok = any(v == "ok" for v in checks.values())

        if all_ok:
            overall = "healthy"
        elif any_ok:
            overall = "degraded"
        else:
            overall = "unhealthy"

        return {
            "status": overall,
            "checks": checks,
            "version": settings.api_version,
        }

    return application


# Create the application instance for uvicorn
app = create_app()
