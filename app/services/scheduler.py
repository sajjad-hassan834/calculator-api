from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger
from app.core.settings import settings

scheduler = AsyncIOScheduler()

def heartbeat_task():
    logger.debug("Scheduler heartbeat: Checking for scheduled tasks (e.g., publishing)")

def start_scheduler():
    if not settings.scheduler_enabled:
        logger.info("Scheduler is disabled in settings")
        return
        
    scheduler.add_job(
        heartbeat_task,
        'interval',
        seconds=settings.scheduler_check_interval_seconds,
        id='heartbeat_job',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("APScheduler started successfully")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("APScheduler stopped")
