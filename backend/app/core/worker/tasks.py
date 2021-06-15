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
    chain = load_entries.s() | pocket_updater.s() | send_messages.s()
    chain()


@app_celery.task()
def load_entries(*args: Any, **kwargs: Any) -> None:
    logger.info("Загрузим новые записи...")

    async def async_task() -> None:
        database = Database(url=config.db.url, paramstyle=config.db.paramstyle)
        await database.connect()
        feeds_repository = FeedsRepository(database)
        feeds_service = FeedsService(repository=feeds_repository)
        users_repository = UsersRepository(database=database)
        users_service = UsersService(repository=users_repository)
        loader = LoadEntries(
            database=database,
            feeds_service=feeds_service,
            users_service=users_service,
        )
        await loader.load(limit_feeds=config.limits.load_feed)
        await database.disconnect()

    asyncio.run(async_task())


@app_celery.task()
def pocket_updater(*args: Any, **kwargs: Any) -> None:
    logger.info("Обновим данные авторизации pocket...")

    async def async_task() -> None:
        database = Database(url=config.db.url, paramstyle=config.db.paramstyle)
        await database.connect()

        pocket_client = PocketClient(
            http_client=HttpClient(),
            consumer_key=config.pocket.consumer_key,
            redirect_url=config.pocket.redirect_url,
        )

        users_repository = UsersRepository(database=database)
        users_service = UsersService(repository=users_repository)
        await pocket.update_access_tokens(
            pocket_client=pocket_client,
            users_service=users_service,
        )
        await database.disconnect()

    asyncio.run(async_task())


@app_celery.task()
def send_messages(*args: Any, **kwargs: Any) -> None:
    logger.info("Отправим новые записи пользователям...")

    async def async_task() -> None:
        database = Database(url=config.db.url, paramstyle=config.db.paramstyle)
        await database.connect()

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
        await sender.send(
            limit_title=config.limits.title,
            limit_text=config.limits.text,
        )
        await database.disconnect()

    asyncio.run(async_task())
