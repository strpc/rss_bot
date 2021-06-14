import asyncio
from typing import Any

from loguru import logger

from app.config import get_config
from app.core.clients.database import Database
from app.core.clients.http_ import HttpClient
from app.core.clients.pocket import PocketClient
from app.core.clients.telegram import Telegram
from app.core.feeds.repository import FeedsRepository
from app.core.feeds.service import FeedsService
from app.core.users.repository import UsersRepository
from app.core.users.service import UsersService
from app.core.worker.load_entries_task.service import LoadEntries
from app.core.worker.pocket_updater_task import service as pocket
from app.core.worker.send_entries_task.service import SenderMessages
from app.core.worker.worker_app import app_celery


config = get_config()


@app_celery.task()
def run_chain() -> None:
    chain = load_articles.s() | pocket_updater.s() | send_messages.s()
    chain()


@app_celery.task()
def load_articles(*args: Any, **kwargs: Any) -> None:
    loop = asyncio.get_event_loop()
    database = Database(url=config.db.url, paramstyle=config.db.paramstyle)
    loop.run_until_complete(database.connect())
    feeds_repository = FeedsRepository(database)
    feeds_service = FeedsService(repository=feeds_repository)
    users_repository = UsersRepository(database=database)
    users_service = UsersService(repository=users_repository)
    loader = LoadEntries(
        database=database,
        feeds_service=feeds_service,
        users_service=users_service,
    )

    try:
        loop.run_until_complete(loader.load(limit_feeds=config.limits.load_feed))
    except Exception as error:
        logger.exception(error)
    finally:
        loop.run_until_complete(database.disconnect())
        loop.close()


@app_celery.task()
def pocket_updater(*args: Any, **kwargs: Any) -> None:
    loop = asyncio.get_event_loop()
    database = Database(url=config.db.url, paramstyle=config.db.paramstyle)
    loop.run_until_complete(database.connect())

    pocket_client = PocketClient(
        http_client=HttpClient(),
        consumer_key=config.pocket.consumer_key,
        redirect_url=config.pocket.redirect_url,
    )

    users_repository = UsersRepository(database=database)
    users_service = UsersService(repository=users_repository)

    try:
        loop.run_until_complete(
            pocket.update_access_tokens(
                pocket_client=pocket_client,
                users_service=users_service,
            ),
        )
    except Exception as error:
        logger.exception(error)
    finally:
        loop.run_until_complete(database.disconnect())
        loop.close()


@app_celery.task()
def send_messages(*args: Any, **kwargs: Any) -> None:
    loop = asyncio.get_event_loop()
    database = Database(url=config.db.url, paramstyle=config.db.paramstyle)
    loop.run_until_complete(database.connect())

    feeds_repository = FeedsRepository(database)
    feeds_service = FeedsService(repository=feeds_repository)

    users_repository = UsersRepository(database=database)
    users_service = UsersService(repository=users_repository)

    telegram = Telegram(token=config.telegram.token, client=HttpClient())

    sender = SenderMessages(
        database=database,
        feeds_service=feeds_service,
        users_service=users_service,
        telegram=telegram,
    )
    try:
        loop.run_until_complete(
            sender.send(
                limit_title=config.limits.title,
                limit_text=config.limits.text,
            ),
        )  # TODO: добавить отключение юзеров, если бот стопнут
    except Exception as error:
        logger.exception(error)
    finally:
        loop.run_until_complete(database.disconnect())
        loop.close()


if __name__ == "__main__":
    send_messages()
