from app.config import MainConfig
from app.endpoints import bot
from app.logger import configure_logging
from easy_notifyer import Telegram
from fastapi import FastAPI

from app import __version__


def init_app() -> FastAPI:
    application = FastAPI(
        version=__version__,
        title="backend",
        docs_url=None,
        redoc_url=None,
    )
    config = init_config()
    application.state.config = config
    configure_logging(config.app.log_level)

    application.include_router(bot.router)

    if not config.app.debug:
        tg = Telegram(
            token=config.telegram.token,
            chat_id=config.telegram.chat_id,
        )
        tg.send_message(f"service {config.telegram.service_name}: started..")
    return application


def init_config() -> MainConfig:
    return MainConfig()


app: FastAPI = init_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, access_log=False)
