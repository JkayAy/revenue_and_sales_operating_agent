from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from playbook_engine import PlaybookEngine, load_playbook_config

from sales_api.config import settings
from sales_api.database import check_database, load_flags_from_db
from sales_api.observability import configure_logging, tracing_middleware
from sales_api.orchestrator import LeadOrchestrator
from sales_api.rate_limit import rate_limit_middleware
from sales_api.routes import admin, health, integrations, leads, webhooks
from sales_api.store import get_flags, sync_flags_from_db


def _playbook_path() -> Path | None:
    repo_root = Path(__file__).resolve().parents[4]
    configured = Path(settings.playbook_config_path)
    if configured.is_absolute():
        return configured if configured.is_file() else None
    candidate = repo_root / configured
    return candidate if candidate.is_file() else None


engine = PlaybookEngine(load_playbook_config(_playbook_path()))
orchestrator = LeadOrchestrator(engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    app.state.flags = get_flags()
    try:
        db_flags = load_flags_from_db()
        if db_flags:
            sync_flags_from_db(db_flags)
            app.state.flags = get_flags()
    except Exception:
        pass
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="PipelinePilot Sales API",
        version="0.5.0",
        description="Revenue & sales operations agent — HubSpot, webhooks, rate limits, tracing",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def admin_api_key_guard(request: Request, call_next):
        if settings.admin_api_key and request.url.path.startswith("/v1/admin"):
            key = request.headers.get("x-admin-key") or request.headers.get("X-Admin-Key")
            if key != settings.admin_api_key:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Invalid or missing admin API key"},
                )
        return await call_next(request)

    @app.middleware("http")
    async def rate_limit_guard(request: Request, call_next):
        return await rate_limit_middleware(request, call_next)

    @app.middleware("http")
    async def trace_requests(request: Request, call_next):
        return await tracing_middleware(request, call_next)

    app.state.settings = settings
    app.state.playbook_engine = engine
    app.state.orchestrator = orchestrator
    app.state.flags = get_flags()

    app.include_router(health.router)
    app.include_router(leads.router, prefix="/v1")
    app.include_router(integrations.router, prefix="/v1")
    app.include_router(webhooks.router, prefix="/v1")
    app.include_router(admin.router, prefix="/v1")
    return app


app = create_app()


def run() -> None:
    import uvicorn

    uvicorn.run(
        "sales_api.main:app",
        host=settings.sales_api_host,
        port=settings.sales_api_port,
        reload=True,
    )
