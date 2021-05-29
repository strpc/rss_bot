import itertools
from typing import Optional, Tuple

from app.core.clients.database import Database


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

    async def get_active_feeds(self, chat_id: int) -> Optional[Tuple[str, ...]]:
        query = f"""
        SELECT url
        FROM bot_users_rss
        WHERE chat_id_id = {self._paramstyle}
        AND active = True
        """
        rows = await self._db.fetchall(query, (chat_id,))
        if rows is not None:
            return tuple(itertools.chain.from_iterable(rows))

    async def disable_feed(self, url: str, chat_id: int) -> None:
        query = f"""
        UPDATE bot_users_rss
        SET active = False
        WHERE url = {self._paramstyle}
        AND chat_id_id = {self._paramstyle}
        """
        await self._db.execute(query, (url, chat_id))
