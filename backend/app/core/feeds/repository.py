import itertools
from typing import Optional, Tuple

from app.core.clients.database import Database


class FeedsRepository:
    def __init__(self, database: Database):
        self._db = database

    async def exists_active_feed_user(self, chat_id: int, url: str) -> bool:
        like_url = f"%{url}%"
        query = """
        SELECT 1
        FROM bot_users_rss
        WHERE url LIKE ?
        AND chat_id_id = ?
        AND active = True
        LIMIT 1
        """
        row = await self._db.fetchone(query, (like_url, chat_id))
        return bool(row)

    async def add_feed(self, url: str, chat_id: int, hash_url_chat_id: str) -> None:
        query = """
        INSERT INTO bot_users_rss (url, chat_id_id, chatid_url_hash, added, active)
        VALUES (?, ?, ?, datetime('now'), true)
        ON CONFLICT (chatid_url_hash) DO UPDATE SET active = true
        """
        await self._db.execute(query, (url, chat_id, hash_url_chat_id))

    async def get_active_feeds(self, chat_id: int) -> Optional[Tuple[str, ...]]:
        query = """
        SELECT url
        FROM bot_users_rss
        WHERE chat_id_id = ?
        AND active = True
        """
        rows = await self._db.fetchall(query, (chat_id,))
        if rows is not None:
            return tuple(itertools.chain.from_iterable(rows))
