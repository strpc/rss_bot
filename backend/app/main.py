from typing import Callable

from app import __version__
from app.config import MainConfig
from app.core.clients.database import Database
from app.endpoints import callback, message
from app.logger import configure_logging
from easy_notifyer import Telegram
from fastapi import FastAPI, Response
from fastapi.exceptions import RequestValidationError
from loguru import logger


def init_app() -> FastAPI:
    application = FastAPI(
        version=__version__,
        title="backend",
        docs_url=None,
        redoc_url=None,
    )
    config = init_config()
    configure_logging(config.app.log_level)

    application.state.config = config
    application.state.db = Database(config.db.path)

    application.add_event_handler("startup", startup_event(application))
    application.add_event_handler("shutdown", shutdown_event(application))

    application.add_exception_handler(RequestValidationError, validation_exception_handler)

    application.include_router(message.router, prefix="/message")
    application.include_router(callback.router, prefix="/callback")

    if not config.app.debug:
        logger.info("Service is started.")
        tg = Telegram(
            token=config.easy_notifyer.token,
            chat_id=config.easy_notifyer.chat_id,
        )
        tg.send_message(f"service {config.easy_notifyer.service_name}: started..")
    else:
        logger.info("Debug is enabled.")
    return application


def init_config() -> MainConfig:
    return MainConfig()


async def validation_exception_handler(request, exc):
    logger.error(str(exc))
    return Response(status_code=200)


def startup_event(application: FastAPI) -> Callable:
    async def startup():
        await application.state.db.connect()

    return startup


def shutdown_event(application: FastAPI) -> Callable:
    async def shutdown():
        await application.state.db.disconnect()

    return shutdown


app: FastAPI = init_app()
