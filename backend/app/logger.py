import sys

from loguru import logger

from app.config import LogLevelEnum


def configure_logging(log_level: LogLevelEnum) -> None:
    logger.remove()
    fmt = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "chat_id={extra[chat_id]} | "
        # "username={extra[username]} | "
        "uuid={extra[uuid]} | - <level>{message}</level>"
    )
    if not log_level.DEBUG:
        logger.add("docker/logs/backend.log", rotation="10 MB", level=log_level, format=fmt)
    logger.add(sys.stdout, level=log_level, format=fmt)
    logger.configure(extra={"chat_id": 0, "username": '""', "uuid": '""'})
