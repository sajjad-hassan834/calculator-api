from functools import lru_cache

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.settings import settings


@lru_cache
def get_engine():
    if not settings.database_url:
        raise ValueError(
            "DATABASE_URL is not configured. Set it in .env or environment variables."
        )
    return create_engine(
        settings.database_url,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=settings.db_echo,
    )


@lru_cache
def get_session_factory():
    return sessionmaker(autocommit=False, autoflush=False, bind=get_engine())


def get_session_local():
    return get_session_factory()


Base = declarative_base()


async def check_database_health() -> dict:
    try:
        eng = get_engine()
        with eng.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.scalar()
        return {"status": "healthy", "database": settings.database_name}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
