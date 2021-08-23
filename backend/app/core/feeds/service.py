from http.client import InvalidURL
from typing import Optional, Tuple
from urllib.error import URLError

import feedparser
from loguru import logger
from pydantic import parse_obj_as

from app.core.feeds.models import Entry, Feed, UserEntry
from app.core.feeds.repository import FeedsRepository
from app.core.utils import run_in_threadpool


class Parser:
    def __init__(self, url: str):
        self._url = url

    def _parse(self, limit: int) -> Optional[Tuple[Entry, ...]]:
        try:
            entries = feedparser.parse(self._url).get("entries")
        except Exception as error:
            logger.exception(error)
            return None

        if entries is None:
            return None
        logger.debug("Все загруженные записи: {}", entries[:limit][::-1])
        return parse_obj_as(Tuple[Entry, ...], entries[:limit][::-1])

    async def parse(self, limit: int) -> Optional[Tuple[Entry, ...]]:
        return await run_in_threadpool(self._parse, limit)


class FeedsService:
    def __init__(self, repository: FeedsRepository):
        self._repository = repository

    async def exists_active_feed_user(self, chat_id: int, url: str) -> bool:
        return await self._repository.exists_active_feed_user(chat_id=chat_id, url=url)

    @staticmethod
    async def validate_feed(url: str) -> bool:
        logger.debug("Проверяем валидность фида {}...", url)
        try:
            return bool((await run_in_threadpool(feedparser.parse, url)).get("entries"))
        except (URLError, InvalidURL):
            logger.warning("Фид невалиден {}", url)
            return False

    async def add_new_feed_user(self, chat_id: int, url: str) -> None:
        await self.add_feed(url)
        await self.add_user_feed(url, chat_id)

    async def add_user_feed(self, url: str, chat_id: int) -> None:
        return await self._repository.add_user_feed(url=url, chat_id=chat_id)

    async def add_feed(self, url: str) -> None:
        return await self._repository.add_feed(url)

    async def exists_entry(self, url: str) -> bool:
        return await self._repository.exists_entry(url)

    async def disable_feed(self, url: str, chat_id: int) -> None:
        return await self._repository.disable_feed(url=url, chat_id=chat_id)

    async def get_active_feeds(self, chat_id: int) -> Optional[Tuple[Feed, ...]]:
        return await self._repository.get_active_feeds(chat_id=chat_id)

    @staticmethod
    async def load_entries(url: str, limit_feeds: int) -> Optional[Tuple[Entry, ...]]:
        parser = Parser(url)
        return await parser.parse(limit_feeds)

    async def exists_user_entry(self, chat_id: int, url: str) -> bool:
        return await self._repository.exists_user_entry(chat_id=chat_id, url=url)

    async def insert_entry(self, entry: Entry, url_feed: str) -> None:
        return await self._repository.insert_entry(entry, url_feed)

    async def insert_user_entry(self, url: str, chat_id: int) -> None:
        return await self._repository.insert_user_entry(url, chat_id)

    async def get_unsended_entries(self) -> Optional[Tuple[UserEntry, ...]]:
        return await self._repository.get_unsended_entries()

    async def mark_sended_entry(self, entry_id: int) -> None:
        return await self._repository.mark_sended_entries(entry_id)
