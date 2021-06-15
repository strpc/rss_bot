from typing import Any, List, Optional, Tuple

from pydantic import parse_obj_as

from app.core.clients.database import Database
from app.core.feeds.models import Feed, UserEntry


class FeedsRepository:
    def __init__(self, database: Database):
        self._db = database
        self._paramstyle = self._db.paramstyle

    async def exists_active_feed_user(self, chat_id: int, url: str) -> bool:
        like_url = f"%{url}%"
        query = f"""
        SELECT 1
        FROM bot_users_rss
        WHERE url LIKE {self._paramstyle}
        AND chat_id_id = {self._paramstyle}
        AND active = True
        LIMIT 1
        """
        row = await self._db.fetchone(query, (like_url, chat_id))
        return bool(row)

    async def add_feed(self, url: str, chat_id: int, hash_url_chat_id: str) -> None:
        query = f"""
        INSERT INTO bot_users_rss (url, chat_id_id, chatid_url_hash, added, active)
        VALUES ({self._paramstyle}, {self._paramstyle}, {self._paramstyle}, datetime('now'), true)
        ON CONFLICT (chatid_url_hash) DO UPDATE SET active = true
        """
        await self._db.execute(query, (url, chat_id, hash_url_chat_id))

    async def disable_feed(self, url: str, chat_id: int) -> None:
        query = f"""
        UPDATE bot_users_rss
        SET active = False
        WHERE url = {self._paramstyle}
        AND chat_id_id = {self._paramstyle}
        """
        await self._db.execute(query, (url, chat_id))

    async def get_active_feeds(self, chat_id: int) -> Optional[Tuple[Feed, ...]]:
        query = f"""
        SELECT
        url,
        chatid_url_hash as chat_id_url_hash
        FROM bot_users_rss
        WHERE chat_id_id = {self._paramstyle}
        AND active = True
        """
        rows = await self._db.fetchall(query, (chat_id,), as_dict=True)
        if rows is not None:
            return parse_obj_as(Tuple[Feed, ...], rows)

    async def exists_entry(self, chat_id_url_hash: str) -> bool:
        query = f"""
        SELECT 1
        FROM bot_article
        WHERE
        chatid_url_article_hash = {self._paramstyle}
        """
        row = await self._db.fetchone(query, (chat_id_url_hash,))
        return bool(row)

    async def insert_entries(self, values: List[Tuple[Any, ...]]) -> None:
        query = f"""
        INSERT INTO bot_article (
        url_article, title, text, chatid_url_article_hash, rss_url_id, chat_id_id, added, sended
        )
        VALUES ({self._paramstyle}, {self._paramstyle}, {self._paramstyle}, {self._paramstyle},
        {self._paramstyle}, {self._paramstyle}, datetime('now'), False)
        """
        await self._db.executemany(query, values)

    async def get_unsended_entries(self) -> Optional[Tuple[UserEntry, ...]]:
        query = """
        SELECT
        id,
        title as title,
        url_article as url,
        text as text,
        chat_id_id as chat_id
        FROM bot_article
        WHERE sended is FALSE
        """
        rows = await self._db.fetchall(query, as_dict=True)
        if rows is not None:
            return parse_obj_as(Tuple[UserEntry, ...], rows)

    async def mark_sended_entries(self, entry_id: int) -> None:
        query = f"""
        UPDATE bot_article
        SET
        sended = TRUE
        WHERE id = {self._paramstyle}
        """
        await self._db.execute(query, (entry_id,))
