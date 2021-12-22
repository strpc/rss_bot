from typing import Callable

from easy_notifyer import Telegram
from fastapi import FastAPI, Request, Response, status
from fastapi.exceptions import RequestValidationError
from loguru import logger

from app import __version__
from app.api import deps
from app.api.endpoints import healthcheck
from app.api.endpoints.update import views as updates
from app.config import MainConfig
from app.containers import Container
from app.logger import configure_logging


BASE_URL = "/rss_bot/backend"


def init_app() -> FastAPI:
    application = FastAPI(
        version=__version__,
        title="backend",
        docs_url=None,
        redoc_url=None,
    )
    container = Container()
    container.config.from_pydantic(MainConfig())
    container.init_resources()
    container.wire(modules=[deps, updates])
    application.state.container = container

    configure_logging(container.config.app.log_level())

    application.state.db = container.database()

    application.add_event_handler("startup", startup_event(application))
    application.add_event_handler("shutdown", shutdown_event(application))

    application.add_exception_handler(RequestValidationError, validation_exception_handler)

    application.include_router(updates.router, prefix=BASE_URL)
    application.include_router(healthcheck.router, prefix=f"{BASE_URL}/healthcheck")

    if not container.config.app.debug():
        logger.info("Service is started.")
        tg = Telegram(
            token=container.config.easy_notifyer.token(),
            chat_id=container.config.easy_notifyer.chat_id(),
        )
        tg.send_message(f"service {container.config.easy_notifyer.service_name()}: started..")
    else:
        logger.info("Debug is enabled.")
    return application


async def validation_exception_handler(_: Request, exc: RequestValidationError) -> Response:
    logger.error(str(exc))
    return Response(status_code=status.HTTP_200_OK)


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
