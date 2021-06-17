import sys

from loguru import logger

from app.config import LogLevelEnum


def configure_logging(log_level: LogLevelEnum) -> None:
    logger.remove()
    if log_level is not LogLevelEnum.DEBUG:
        logger.add("docker/logs/worker.log", rotation="10 MB", level=log_level)
    else:
        logger.add("docker/logs/worker_debug.log", rotation="10 MB", level=log_level)
    logger.add(sys.stdout, level=log_level)
