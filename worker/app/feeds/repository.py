from typing import Any, List, Optional, Tuple

from pydantic import parse_obj_as

from app.clients.database import Database
from app.feeds.models import Feed


class FeedsRepository:
    def __init__(self, db: Database, paramstyle: str):
        self._db = db
        self._paramstyle = paramstyle

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
