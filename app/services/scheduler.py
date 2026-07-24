from datetime import UTC, datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger
from sqlalchemy import text

from app.core.settings import settings
from app.database.connection import get_session_factory
from app.services.ai_research_agent import AIResearchAgent
from app.services.ai_seo_agent import AISEOAgent
from app.models.ai_agent import AIResearchTask, AIGeneratedContent, ContentCalendar, SEOAudit

scheduler = AsyncIOScheduler()
research_agent = AIResearchAgent()
seo_agent = AISEOAgent()


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


async def run_daily_ai_research():
    logger.info("Running daily autonomous AI research...")
    session_factory = get_session_factory()
    db = session_factory()
    try:
        # Example trending topic logic
        topic = "Top 5 financial habits to adopt in 2026"
        research_result = await research_agent.conduct_research(topic)
        task = AIResearchTask(topic=topic, niche="Personal Finance", research_data=research_result, status="completed")
        db.add(task)
        db.commit()
        
        content_html = await research_agent.generate_blog_post(topic=topic, research_data=research_result)
        content = AIGeneratedContent(research_task_id=task.id, content_type="blog_post", title=topic, content=content_html, status="draft")
        db.add(content)
        db.commit()
        
        calendar = ContentCalendar(content_id=content.id, status="pending_approval")
        db.add(calendar)
        db.commit()
        logger.info(f"Successfully generated AI research and draft for: {topic}")
    except Exception as e:
        logger.error(f"Failed daily AI research: {e}")
        db.rollback()
    finally:
        db.close()

async def run_nightly_seo_audit():
    logger.info("Running nightly autonomous SEO audit...")
    session_factory = get_session_factory()
    db = session_factory()
    try:
        pages = [{"url": "/", "title": "Home", "content": "Welcome to FinanceCalculator"}]
        audit_results = await seo_agent.audit_pages(pages)
        audit = SEOAudit(target_url="global", audit_results=audit_results, score=audit_results.get("overall_score", 0), recommendations=audit_results.get("recommendations", []))
        db.add(audit)
        db.commit()
        logger.info("Successfully completed nightly SEO audit")
    except Exception as e:
        logger.error(f"Failed nightly SEO audit: {e}")
        db.rollback()
    finally:
        db.close()

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
    
    # Run daily at 6 AM
    scheduler.add_job(
        run_daily_ai_research,
        'cron',
        hour=6,
        minute=0,
        id='daily_ai_research',
        replace_existing=True,
    )
    
    # Run nightly at 2 AM
    scheduler.add_job(
        run_nightly_seo_audit,
        'cron',
        hour=2,
        minute=0,
        id='nightly_seo_audit',
        replace_existing=True,
    )

    scheduler.start()
    logger.info("APScheduler started successfully")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("APScheduler stopped")
