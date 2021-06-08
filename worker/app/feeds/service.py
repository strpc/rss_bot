from typing import Any, List, Optional, Tuple

import feedparser
from loguru import logger
from pydantic import parse_obj_as

from app.feeds.models import Entry, Feed, UserEntry
from app.feeds.repository import FeedsRepository
from app.utils import run_in_threadpool


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

        return parse_obj_as(Tuple[Entry, ...], entries[:limit])

    async def parse(self, limit: int) -> Optional[Tuple[Entry, ...]]:
        return await run_in_threadpool(self._parse, limit)


class FeedsService:
    def __init__(self, *, repository: FeedsRepository):
        self._repository = repository

    async def get_active_feeds(self, chat_id: int) -> Optional[Tuple[Feed, ...]]:
        return await self._repository.get_active_feeds(chat_id=chat_id)

    @staticmethod
    async def load_entries(url: str, limit_feeds: int) -> Optional[Tuple[Entry, ...]]:
        parser = Parser(url)
        return await parser.parse(limit_feeds)

    async def exists_entry(self, chat_id_url_hash: str) -> bool:
        return await self._repository.exists_entry(chat_id_url_hash=chat_id_url_hash)

    async def insert_entries(self, values: List[Tuple[Any, ...]]) -> None:
        return await self._repository.insert_entries(values)

    async def get_unsended_entries(self) -> Optional[Tuple[UserEntry, ...]]:
        return await self._repository.get_unsended_entries()

    async def mark_sended_entries(self, entries_id: List[int]) -> None:
        return await self._repository.mark_sended_entries(entries_id)
