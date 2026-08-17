"""OpenSignal API - FastAPI entry point (Render: uvicorn main:app)."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.analytics.routes import router as analytics_router
from app.auth.routes import router as auth_router
from app.campaigns.routes import router as campaigns_router
from app.crm.routes import router as crm_router
from app.email.routes import router as email_router
from app.email.webhooks import router as webhooks_router
from app.middleware.rate_limit import RateLimitMiddleware
from app.settings.routes import router as settings_router
from app.signals.routes import router as signals_router
from app.services.base import ServiceError
from config import settings

logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))
logger = logging.getLogger("opensignal")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.sentry_dsn:
        import sentry_sdk

        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.environment,
            traces_sample_rate=0.1,
        )
        logger.info("Sentry initialized")

    if not settings.is_production:
        try:
            from app.database.models import Base
            from app.database.session import engine

            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Development mode: ensured tables exist")
        except Exception as exc:  # noqa: BLE001
            logger.warning("Skipped auto-create tables (is DATABASE_URL set?): %s", exc)
    yield


app = FastAPI(
    title="OpenSignal API",
    description="Signal-Based Demand Generation Platform (GTM-360)",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)

API = "/api/v1"
app.include_router(auth_router, prefix=f"{API}/auth", tags=["auth"])
app.include_router(signals_router, prefix=f"{API}", tags=["signals", "accounts"])
app.include_router(campaigns_router, prefix=f"{API}", tags=["campaigns"])
app.include_router(email_router, prefix=f"{API}", tags=["email"])
app.include_router(crm_router, prefix=f"{API}", tags=["crm"])
app.include_router(analytics_router, prefix=f"{API}", tags=["analytics"])
app.include_router(settings_router, prefix=f"{API}", tags=["settings"])
app.include_router(webhooks_router, prefix=f"{API}", tags=["webhooks"])


@app.exception_handler(ServiceError)
async def service_error_handler(request, exc: ServiceError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.get("/health", tags=["system"])
async def health() -> dict:
    return {"status": "ok", "service": "opensignal", "environment": settings.environment}


@app.get("/", tags=["system"])
async def root() -> dict:
    return {"name": "OpenSignal API", "docs": "/docs", "health": "/health"}
