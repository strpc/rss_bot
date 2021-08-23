from typing import AsyncIterator, Optional

from loguru import logger

from app.core.clients.database import Database
from app.core.feeds.models import Entry, Feed
from app.core.feeds.service import FeedsService
from app.core.users.models import User
from app.core.users.service import UsersService


class LoadEntries:
    def __init__(
        self,
        *,
        database: Database,
        feeds_service: FeedsService,
        users_service: UsersService,
    ):
        self._db = database
        self._feeds_service = feeds_service
        self._users_service = users_service

    async def _exists_user_entry(self, chat_id: int, url: Optional[str]) -> bool:
        if url is None:
            logger.warning("Фид без урла. chat_id={}")
        return await self._feeds_service.exists_user_entry(chat_id=chat_id, url=url)  # type: ignore

    async def _load_new_entries(
        self,
        user: User,
        feed: Feed,
        limit_feeds: int,
    ) -> Optional[AsyncIterator[Entry]]:
        logger.debug("Загружаем записи фида {}...", feed.url)
        entries = await self._feeds_service.load_entries(feed.url, limit_feeds)

        if entries is None:
            logger.warning("У фида отсутствуют статьи. {}", feed)
            return

        for entry in entries:
            logger.debug("Проверим существует лм уже запись {} в базе...", entry)
            if await self._exists_user_entry(user.chat_id, entry.url):
                logger.debug("Запись уже есть в базе. Пропускаем...")
                continue
            logger.debug("Запись {} новая. Запишем ее в базу.")
            yield entry

    async def _insert_user_entry(self, chat_id: int, entry: Entry, url_feed: str) -> None:
        if not await self._feeds_service.exists_entry(entry.url):
            await self._feeds_service.insert_entry(entry, url_feed)
        await self._feeds_service.insert_user_entry(entry.url, chat_id)

    async def load(self, limit_feeds: int) -> None:
        logger.debug("Получаем список активных юзеров...")
        active_users = await self._users_service.get_active_users()

        if active_users is None:
            logger.warning("Нет активных юзеров.")
            return

        logger.info("{} активных юзеров", len(active_users))
        for user in active_users:
            logger.info("Загружаем активные фиды юзера {}...", user.chat_id)
            user_feeds = await self._feeds_service.get_active_feeds(user.chat_id)

            if user_feeds is None:
                logger.debug("У юзера {} нет активных фидов.", user)
                continue

            logger.info("У юзера {} - {} активных фидов.", user.chat_id, len(user_feeds))
            for feed in user_feeds:
                async for new_entry in self._load_new_entries(
                    user,
                    feed,
                    limit_feeds,
                ):  # type: ignore
                    await self._insert_user_entry(user.chat_id, new_entry, feed.url)
