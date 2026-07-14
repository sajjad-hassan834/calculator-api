"""Force database schema sync — drops stale alembic_version and re-runs migrations."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database.base import Base
from app.database.connection import get_engine
from app.core.settings import settings
import app.models  # noqa: F401


def sync():
    engine = get_engine()

    # Drop stale alembic_version so migrations run fresh
    with engine.connect() as conn:
        conn.execute(
            text("DROP TABLE IF EXISTS alembic_version")
        )
        conn.commit()

    # Run alembic migrations
    from alembic.config import Config
    from alembic import command
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", settings.database_url)
    command.upgrade(alembic_cfg, "head")
    print("Migrations applied successfully.")


if __name__ == "__main__":
    from sqlalchemy import text
    sync()
