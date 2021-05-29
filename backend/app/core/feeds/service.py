from http.client import InvalidURL
from typing import Optional, Tuple
from urllib.error import URLError

import feedparser
from loguru import logger

from app.core.feeds.repository import FeedsRepository
from app.core.utils import get_hash, run_in_threadpool


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

    async def add_feed(self, url: str, chat_id: int) -> None:
        hash_url_chat_id = get_hash(url, chat_id)
        await self._repository.add_feed(url, chat_id, hash_url_chat_id)

    async def get_active_feeds(self, chat_id: int) -> Optional[Tuple[str, ...]]:
        return await self._repository.get_active_feeds(chat_id)
