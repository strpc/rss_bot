from app.config import LogLevelEnum
from loguru import logger


def configure_logging(log_level: LogLevelEnum):
    logger.add("docker/logs/celery_log.log", rotation="10 MB", level=log_level)
