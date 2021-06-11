import sys

from loguru import logger

from app.config import LogLevelEnum


def configure_logging(log_level: LogLevelEnum) -> None:
    logger.remove()
    if not log_level.DEBUG:
        logger.add("docker/logs/celery.log", rotation="10 MB", level=log_level)
    logger.add(sys.stdout, level=log_level)
