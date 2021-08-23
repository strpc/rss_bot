from typing import Callable, Optional

from easy_notifyer import Telegram
from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from loguru import logger

from app import __version__
from app.api import deps
from app.api.endpoints import message
from app.containers import Container
from app.core.clients.database import Database
from app.logger import configure_logging


def init_app() -> FastAPI:
    application = FastAPI(
        version=__version__,
        title="backend",
        docs_url=None,
        redoc_url=None,
    )
    container = Container()
    container.wire(modules=[deps, message])
    container.init_resources()
    application.state.container = container

    configure_logging(container.config().app.log_level)

    application.state.db = Database(container.config().db.dsn)

    application.add_event_handler("startup", startup_event(application))
    application.add_event_handler("shutdown", shutdown_event(application))

    application.add_exception_handler(RequestValidationError, validation_exception_handler)

    application.include_router(message.router, prefix="/rss_bot/backend")

    if not container.config().app.debug:
        logger.info("Service is started.")
        tg = Telegram(
            token=container.config().easy_notifyer.token,
            chat_id=container.config().easy_notifyer.chat_id,
        )
        tg.send_message(f"service {container.config().easy_notifyer.service_name}: started..")
    else:
        logger.info("Debug is enabled.")
    return application


async def validation_exception_handler(request: Request, exc: Optional[BaseException]) -> Response:
    logger.error(str(exc))
    return Response(status_code=200)


def startup_event(application: FastAPI) -> Callable:
    async def startup() -> None:
        await application.state.db.connect()
        logger.info("Database is connected!")

    return startup


def shutdown_event(application: FastAPI) -> Callable:
    async def shutdown() -> None:
        await application.state.db.disconnect()
        logger.info("Database is disconnected.")

    return shutdown


app: FastAPI = init_app()
