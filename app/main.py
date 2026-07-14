import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.admin import admin_router
from app.api.public import public_router
from app.api.v1 import v1_router
from app.core.logging import setup_logging
from app.core.settings import settings
from app.exceptions import AppException
from app.middleware.cors import setup_cors
from app.middleware.logging import LoggingMiddleware
from app.middleware.security import setup_security
from app.middleware.monitoring import setup_monitoring
from app.middleware.rate_limit import limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from app.schemas.common import error_response


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info(f"Starting {settings.app_name} v{settings.app_version} in {settings.app_env} mode")
    if settings.is_development:
        logger.warning("Running in development mode")
    from app.database.connection import get_engine, get_session_local
    from app.database.base import Base
    import app.models  # noqa: F401 — register all models with Base.metadata
    engine = get_engine()

    # Run schema migrations
    try:
        from alembic.config import Config
        from alembic import command
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", settings.database_url)
        command.upgrade(alembic_cfg, "head")
        logger.info("Alembic migrations applied")
    except Exception as e:
        logger.warning(f"Alembic migration failed ({e}), falling back to create_all")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables synchronized via create_all")

    session_factory = get_session_local()
    db = session_factory()
    try:
        from app.seeds.roles import seed_roles
        seed_roles(db)
    finally:
        db.close()
    from app.services.cache import get_cache, close_cache
    from app.services.scheduler import start_scheduler, stop_scheduler
    
    get_cache()  # Initialize cache connection
    start_scheduler()  # Start APScheduler
    
    yield
    
    stop_scheduler()
    close_cache()
    logger.info("Shutting down application")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="FinanceCalculator API — Production-ready financial platform backend",
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
    lifespan=lifespan,
)

setup_cors(app)
setup_security(app)
app.add_middleware(LoggingMiddleware)

uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

app.include_router(v1_router)
app.include_router(admin_router)
app.include_router(public_router)

setup_monitoring(app)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            message=exc.detail.get("message", "Application error"),
            errors=exc.detail.get("errors", []),
            code=exc.detail.get("code", "APP_ERROR"),
        ),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        loc = " -> ".join(str(l) for l in err.get("loc", []))
        msg = err.get("msg", "")
        errors.append(f"{loc}: {msg}")
    return JSONResponse(
        status_code=422,
        content=error_response(
            message="Validation error",
            errors=errors,
            code="VALIDATION_ERROR",
        ),
    )


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    logger.error(f"Database integrity error: {str(exc)}")
    return JSONResponse(
        status_code=409,
        content=error_response(
            message="Database constraint violation",
            errors=[str(exc.orig)],
            code="DUPLICATE_ENTRY",
        ),
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            message=str(exc.detail) if exc.detail else "HTTP error",
            code=f"HTTP_{exc.status_code}",
        ),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=error_response(
            message="Internal server error",
            code="INTERNAL_ERROR",
        ),
    )


@app.get("/")
def root():
    from app.schemas.common import success_response
    return success_response(
        data={
            "app": settings.app_name,
            "version": settings.app_version,
            "environment": settings.app_env,
        },
        message="Welcome to FinanceCalculator API",
    )
