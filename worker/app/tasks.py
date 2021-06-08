import asyncio
from typing import Any

from loguru import logger

from app.clients.database import Database
from app.clients.http_ import HttpClient
from app.clients.pocket import PocketClient
from app.clients.telegram import Telegram
from app.config import get_config
from app.feeds.repository import FeedsRepository
from app.feeds.service import FeedsService
from app.load_entries_task.service import LoadEntries
from app.logger import configure_logging
from app.main import app_celery
from app.pocket.service import PocketService
from app.pocket_updater_task.service import PocketUpdater
from app.send_entries_task.service import SenderMessages
from app.users.repository import UsersRepository
from app.users.service import UsersService


config = get_config()
configure_logging(config.app.log_level)


@app_celery.task()
def load_articles(*args: Any, **kwargs: Any) -> None:
    loop = asyncio.get_event_loop()
    db = Database(url=config.db.url, paramstyle=config.db.paramstyle)
    loop.run_until_complete(db.connect())
    feeds_repository = FeedsRepository(db)
    feeds_service = FeedsService(repository=feeds_repository)
    users_repository = UsersRepository(db=db)
    users_service = UsersService(repository=users_repository)
    loader = LoadEntries(db=db, feeds_service=feeds_service, users_service=users_service)

    try:
        loop.run_until_complete(loader.load(limit_feeds=config.app.limit_load_feed))
    except Exception as error:
        logger.exception(error)
    finally:
        loop.run_until_complete(db.disconnect())
        loop.close()


@app_celery.task()
def pocket_updater(*args: Any, **kwargs: Any) -> None:
    loop = asyncio.get_event_loop()
    db = Database(url=config.db.url, paramstyle=config.db.paramstyle)
    loop.run_until_complete(db.connect())

    pocket_client = PocketClient(http_client=HttpClient(), consumer_key=config.pocket.consumer_key)
    pocket_service = PocketService(client=pocket_client)

    users_repository = UsersRepository(db=db)
    users_service = UsersService(repository=users_repository)

    updater = PocketUpdater(pocket_service=pocket_service, users_service=users_service)
    try:
        loop.run_until_complete(updater.update())
    except Exception as error:
        logger.exception(error)
    finally:
        loop.run_until_complete(db.disconnect())
        loop.close()


def send_messages(*args: Any, **kwargs: Any) -> None:
    loop = asyncio.get_event_loop()
    db = Database(url=config.db.url, paramstyle=config.db.paramstyle)
    loop.run_until_complete(db.connect())

    feeds_repository = FeedsRepository(db)
    feeds_service = FeedsService(repository=feeds_repository)

    users_repository = UsersRepository(db=db)
    users_service = UsersService(repository=users_repository)

    telegram = Telegram(token=config.telegram.token, client=HttpClient())

    sender = SenderMessages(
        db=db,
        feeds_service=feeds_service,
        users_service=users_service,
        telegram=telegram,
    )
    try:
        loop.run_until_complete(sender.send())
    except Exception as error:
        logger.exception(error)
    finally:
        loop.run_until_complete(db.disconnect())
        loop.close()


if __name__ == "__main__":
    send_messages()
