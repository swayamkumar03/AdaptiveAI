"""
app/main.py
FastAPI application factory with lifespan management.
"""
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.db.init_db import init_db

# ---------------------------------------------------------------------------
# Structured logging setup
# ---------------------------------------------------------------------------
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer() if settings.debug else structlog.processors.JSONRenderer(),
    ]
)
logger = structlog.get_logger()


# ---------------------------------------------------------------------------
# Lifespan — startup / shutdown
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan context manager.
    - Startup: enable pgvector, seed super admin
    - Shutdown: close DB connections (handled by engine disposal)
    """
    logger.info(
        "AdaptiveAI starting up",
        env=settings.app_env,
        version=settings.app_version,
        ai_provider=settings.ai_provider,
    )
    await init_db()
    yield
    logger.info("AdaptiveAI shutting down.")


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------
def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "Multi-tenant enterprise conversational AI platform "
            "with RAG, confidence checking, and continuous improvement."
        ),
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan,
    )

    # ── CORS ──────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins + [
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
            "http://localhost:5173",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
        ],
        allow_origin_regex=r"https?://.*" if settings.debug else None,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ───────────────────────────────────────────────────────────
    # Imported here to avoid circular imports at module load time
    from app.api.v1.router import api_router
    app.include_router(api_router, prefix="/api/v1")

    # ── Global exception handler ───────────────────────────────────────────
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.error("Unhandled exception", path=request.url.path, error=str(exc))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred. Please try again."},
        )

    # ── Health check ──────────────────────────────────────────────────────
    @app.get("/health", tags=["Health"], summary="Health check")
    async def health() -> dict[str, str]:
        return {
            "status": "ok",
            "version": settings.app_version,
            "env": settings.app_env,
        }

    # ── Widget Script & Demo Page ──────────────────────────────────────────
    import os
    from fastapi.responses import FileResponse

    frontend_public = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "frontend", "public")
    )

    @app.get("/widget.js", include_in_schema=False)
    async def get_widget_js():
        widget_file = os.path.join(frontend_public, "widget.js")
        if os.path.exists(widget_file):
            return FileResponse(widget_file, media_type="application/javascript")
        return JSONResponse(status_code=404, content={"detail": "widget.js not found"})

    @app.get("/demo", include_in_schema=False)
    async def get_demo_html():
        demo_file = os.path.join(frontend_public, "demo.html")
        if os.path.exists(demo_file):
            return FileResponse(demo_file, media_type="text/html")
        return JSONResponse(status_code=404, content={"detail": "demo.html not found"})

    return app


app = create_app()
