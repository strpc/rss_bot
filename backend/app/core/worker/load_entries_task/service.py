from typing import AsyncIterator, Optional

from loguru import logger

from app.core.clients.database import Database
from app.core.feeds.models import Entry, UserFeed
from app.core.feeds.service import FeedsService


class LoadEntries:
    def __init__(
        self,
        *,
        database: Database,
        feeds_service: FeedsService,
    ):
        self._db = database
        self._feeds_service = feeds_service

    async def _exists_user_entry(self, chat_id: int, url: Optional[str]) -> bool:
        if url is None:
            logger.warning("Фид без урла. chat_id={}")
        return await self._feeds_service.exists_user_entry(chat_id=chat_id, url=url)  # type: ignore

    async def _get_new_entries(
        self,
        feed_user: UserFeed,
        limit_feeds: int,
    ) -> Optional[AsyncIterator[Entry]]:
        logger.debug("Загружаем записи фида {}...", feed_user.url)
        entries = await self._feeds_service.load_entries(feed_user.url, limit_feeds)

        if entries is None:
            logger.warning("У фида отсутствуют статьи. {}", feed_user.url)
            return

        for entry in entries:
            logger.debug("Проверим существует лм уже запись {} в базе...", entry)
            if await self._exists_user_entry(feed_user.chat_id, entry.url):
                logger.debug("Запись уже есть в базе. Пропускаем...")
                continue
            logger.debug("Запись {} новая. Запишем ее в базу.", entry)
            yield entry

    async def _insert_user_entry(
        self,
        chat_id: int,
        entry: Entry,
        url_feed: str,
    ) -> None:
        if not await self._feeds_service.exists_entry(entry.url):
            await self._feeds_service.insert_entry(entry, url_feed)
        await self._feeds_service.insert_user_entry(entry.url, chat_id)

    async def load(self, limit_feeds: int) -> None:
        logger.debug("Получаем список активных юзеров и их фиды...")
        active_rss_users = await self._feeds_service.get_active_feeds_users()

        if active_rss_users is None:
            logger.warning("Нет активных юзеров.")
            return

        logger.info("{} фидов для проверки на новые записи", len(active_rss_users))
        for feed_user in active_rss_users:
            logger.info(
                "Загружаем фид {} юзера {}...",
                feed_user.url[:30],
                feed_user.chat_id,
            )
            async for new_entry in self._get_new_entries(feed_user, limit_feeds):  # type: ignore
                await self._insert_user_entry(
                    feed_user.chat_id,
                    new_entry,
                    feed_user.url,
                )
