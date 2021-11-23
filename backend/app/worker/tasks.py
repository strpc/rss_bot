import asyncio
from typing import Any

from loguru import logger

from app.clients.database import Database
from app.clients.http_ import HttpClient
from app.clients.pocket import PocketClient
from app.clients.telegram import Telegram
from app.config import MainConfig, get_config
from app.core.feeds.repository import FeedsRepository
from app.core.feeds.service import FeedsService
from app.core.integration.pocket import PocketIntegration
from app.core.integration.repository import PocketRepository
from app.core.users.repository import UsersRepository
from app.core.users.service import UsersService
from app.worker.load_entries_task.service import LoadEntries
from app.worker.pocket_updater_task import service as pocket
from app.worker.send_entries_task.service import SenderMessages
from app.worker.worker_app import app_celery


@app_celery.task(ignore_result=True)
def run_chain() -> None:
    chain = load_entries.s() | pocket_updater.s() | send_messages.s()
    chain()


@app_celery.task(ignore_result=True)
def load_entries(*args: Any, **kwargs: Any) -> None:
    logger.info("Загрузим новые записи...")

    async def async_task(config: MainConfig) -> None:
        database = Database(url=config.db.dsn)
        await database.connect()
        feeds_repository = FeedsRepository(database)
        feeds_service = FeedsService(repository=feeds_repository)
        loader = LoadEntries(
            database=database,
            feeds_service=feeds_service,
        )
        await loader.load(limit_feeds=config.limits.load_feed)
        await database.disconnect()
        return None

    _config = get_config()
    return asyncio.run(async_task(_config))


@app_celery.task(ignore_result=True)
def pocket_updater(*args: Any, **kwargs: Any) -> None:
    logger.info("Обновим данные авторизации pocket...")

    async def async_task(config: MainConfig) -> None:
        database = Database(url=config.db.dsn)
        await database.connect()

        pocket_client = PocketClient(
            http_client=HttpClient(),
            consumer_key=config.pocket.consumer_key,
            redirect_url=config.pocket.redirect_url,
        )

        users_repository = UsersRepository(database=database)
        users_service = UsersService(repository=users_repository)

        pocket_repository = PocketRepository(database=database)
        pocket_integration = PocketIntegration(
            pocket_client=pocket_client,
            users_service=users_service,
            repository=pocket_repository,
        )
        await pocket.update_access_tokens(
            pocket_client=pocket_client,
            pocket_integration=pocket_integration,
        )
        await database.disconnect()
        return None

    _config = get_config()
    if _config.pocket.consumer_key is None:
        logger.info("Pocket consumer key is not set. Exit...")
        return None

    return asyncio.run(async_task(_config))


@app_celery.task(ignore_result=True)
def send_messages(*args: Any, **kwargs: Any) -> None:
    logger.info("Отправим новые записи пользователям...")

    async def async_task(config: MainConfig) -> None:
        database = Database(url=config.db.dsn)
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
            limit_title=config.limits.title_message,
            limit_text=config.limits.text_message,
        )
        await database.disconnect()

    _config = get_config()
    return asyncio.run(async_task(_config))
