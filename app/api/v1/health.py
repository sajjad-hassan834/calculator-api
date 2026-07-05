from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.database.connection import check_database_health
from app.database.session import get_db
from app.schemas.common import success_response

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check():
    return success_response(
        data={
            "status": "healthy",
            "app": settings.app_name,
            "version": settings.app_version,
            "environment": settings.app_env,
        },
        message="Service is healthy",
    )


@router.get("/health/database")
def database_health(db: Session = Depends(get_db)):
    import time
    start = time.time()
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        elapsed = time.time() - start
        return success_response(
            data={
                "status": "healthy",
                "database": settings.database_name,
                "response_time_ms": round(elapsed * 1000, 2),
            },
            message="Database connection is healthy",
        )
    except Exception as e:
        return {
            "success": False,
            "message": "Database connection failed",
            "data": {"status": "unhealthy", "error": str(e)},
        }


@router.get("/health/storage")
def storage_health():
    return success_response(
        data={
            "status": "healthy",
            "provider": "Supabase Storage",
            "buckets": ["media", "avatars", "uploads", "exports", "temp"],
        },
        message="Storage service is configured",
    )


@router.get("/version")
def version():
    return success_response(
        data={
            "version": settings.app_version,
            "app": settings.app_name,
            "environment": settings.app_env,
        },
    )
