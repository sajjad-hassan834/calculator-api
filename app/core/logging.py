import sys
from pathlib import Path

from loguru import logger

from app.core.settings import settings


def setup_logging():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logger.remove()

    logger.add(
        sys.stdout,
        format=settings.log_format,
        level=settings.log_level,
        colorize=True,
    )

    logger.add(
        log_dir / "app_{time:YYYY-MM-DD}.log",
        format=settings.log_format,
        level="DEBUG",
        rotation="1 day",
        retention="30 days",
        compression="gz",
    )

    logger.add(
        log_dir / "error_{time:YYYY-MM-DD}.log",
        format=settings.log_format,
        level="ERROR",
        rotation="1 day",
        retention="90 days",
        compression="gz",
    )

    logger.add(
        log_dir / "audit_{time:YYYY-MM-DD}.log",
        format=settings.log_format,
        level="INFO",
        rotation="1 day",
        retention="365 days",
        compression="gz",
        filter=lambda record: record["extra"].get("audit") is True,
    )

    logger.info("Logging configured", env=settings.app_env)
    return logger
