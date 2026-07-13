from datetime import UTC, datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger
from sqlalchemy import text

from app.core.settings import settings
from app.database.connection import get_session_factory

scheduler = AsyncIOScheduler()


def publish_scheduled_posts():
    """
    Query for blog posts whose scheduled_at has passed but is_published
    is still False, then flip them to published.
    """
    session_factory = get_session_factory()
    db = session_factory()
    try:
        now = datetime.now(UTC)
        result = db.execute(
            text("""
                UPDATE blog_posts
                SET
                    is_published = TRUE,
                    status = 'published',
                    published_at = :now
                WHERE
                    scheduled_at IS NOT NULL
                    AND scheduled_at <= :now
                    AND is_published = FALSE
                    AND deleted_at IS NULL
            """),
            {"now": now},
        )
        db.commit()
        count = result.rowcount
        if count > 0:
            logger.info(f"Scheduler published {count} scheduled blog post(s)")
    except Exception as exc:
        logger.error(f"Scheduler publish failed: {exc}")
        db.rollback()
    finally:
        db.close()


def heartbeat_task():
    logger.debug("Scheduler heartbeat: Checking for scheduled tasks")
    publish_scheduled_posts()


def start_scheduler():
    if not settings.scheduler_enabled:
        logger.info("Scheduler is disabled in settings")
        return

    scheduler.add_job(
        heartbeat_task,
        'interval',
        seconds=settings.scheduler_check_interval_seconds,
        id='heartbeat_job',
        replace_existing=True,
    )

    scheduler.start()
    logger.info("APScheduler started successfully")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("APScheduler stopped")
