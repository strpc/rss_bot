from typing import Optional, Tuple

from pydantic import parse_obj_as

from app.core.clients.database import Database
from app.core.feeds.models import Entry, Feed, UserEntry, UserFeed


class FeedsRepository:
    def __init__(self, database: Database):
        self._db = database
        self._paramstyle = self._db.paramstyle

    async def exists_active_feed_user(self, chat_id: int, url: str) -> bool:
        like_url = f"%{url}%"
        query = f"""
        SELECT 1
        FROM bot_rss_user bru
        JOIN bot_rss br on br.id = bru.rss_id AND br.url LIKE {self._paramstyle}
        JOIN bot_users bu on bru.user_id = bu.id
        WHERE
          bu.chat_id = {self._paramstyle}
          AND bru.active is true
        """
        row = await self._db.fetchone(query, (like_url, chat_id))
        return bool(row)

    async def add_feed(self, url: str) -> None:
        query = f"""
        INSERT INTO bot_rss (url)
        VALUES ({self._paramstyle})
        ON CONFLICT(url) DO NOTHING
        """
        await self._db.execute(query, (url,))

    async def add_user_feed(self, url: str, chat_id: int) -> None:
        query = f"""
        INSERT INTO bot_rss_user (rss_id, user_id, active, added, updated)
        VALUES (
            (SELECT id FROM bot_rss WHERE url = {self._paramstyle}),
            (SELECT id FROM bot_users WHERE chat_id = {self._paramstyle}),
            true,
            datetime('now'),
            datetime('now')
        )
        ON CONFLICT(user_id, rss_id) DO UPDATE SET
            active = true,
            updated = datetime('now')
        """
        await self._db.execute(query, (url, chat_id))

    async def disable_feed(self, url: str, chat_id: int) -> None:
        query = f"""
        UPDATE bot_rss_user
        SET active = False
        WHERE
            rss_id = (SELECT id FROM bot_rss WHERE url = {self._paramstyle})
            AND user_id = (SELECT id FROM bot_users WHERE chat_id = {self._paramstyle})
        """
        await self._db.execute(query, (url, chat_id))

    async def get_active_feeds(self, chat_id: int) -> Optional[Tuple[Feed, ...]]:
        query = f"""
        SELECT url
        FROM bot_rss br
        JOIN bot_rss_user bru on br.id = bru.rss_id
        JOIN bot_users bu on bru.user_id = bu.id
        WHERE
            bru.active is true
            AND bu.chat_id = {self._paramstyle}
        """
        rows = await self._db.fetchall(query, (chat_id,), as_dict=True)
        if rows is not None:
            return parse_obj_as(Tuple[Feed, ...], rows)

    async def get_active_feeds_users(self) -> Optional[Tuple[UserFeed, ...]]:
        query = """
        SELECT
            br.url as url,
            bu.chat_id as chat_id
        FROM bot_rss br
        JOIN bot_rss_user bru on br.id = bru.rss_id
        JOIN bot_users bu on bru.user_id = bu.id
        WHERE
            bu.is_blocked is false
            AND bu.active is true
            AND bru.active is true
        """
        rows = await self._db.fetchall(query, as_dict=True)
        if rows is not None:
            return parse_obj_as(Tuple[UserFeed, ...], rows)

    async def exists_user_entry(self, chat_id: int, url: str) -> bool:
        query = f"""
        SELECT 1
        FROM bot_articles
        JOIN bot_user_articles ON bot_articles.id = bot_user_articles.article_id
        JOIN bot_users ON bot_user_articles.user_id = bot_users.id
        WHERE
            url = {self._paramstyle}
            AND bot_users.chat_id = {self._paramstyle}
        """
        row = await self._db.fetchone(
            query,
            (
                url,
                chat_id,
            ),
        )
        return bool(row)

    async def insert_entry(self, entry: Entry, url_feed: str) -> None:
        query = f"""
        INSERT INTO bot_articles (url, text, added, rss_id, title)
        VALUES (
            {self._paramstyle},
            {self._paramstyle},
            datetime('now'),
            (SELECT id FROM bot_rss WHERE url = {self._paramstyle}),
            {self._paramstyle}
        )
        """
        await self._db.execute(query, (entry.url, entry.text, url_feed, entry.title))

    async def insert_user_entry(self, url: str, chat_id: int) -> None:
        query = f"""
        INSERT INTO bot_user_articles (added, sended, article_id, user_id)
        VALUES (
            datetime('now'),
            false,
            (SELECT id FROM bot_articles WHERE url = {self._paramstyle}),
            (SELECT id FROM bot_users WHERE chat_id = {self._paramstyle})
        )
        """
        await self._db.execute(query, (url, chat_id))

    async def get_unsended_entries(self) -> Optional[Tuple[UserEntry, ...]]:
        query = """
        SELECT
            bot_user_articles.id as id,
            bot_articles.title as title,
            bot_articles.url as url,
            bot_articles.text as text,
            bot_users.chat_id as chat_id
        FROM bot_user_articles
        JOIN bot_users ON bot_user_articles.user_id = bot_users.id
        JOIN bot_articles on bot_user_articles.article_id = bot_articles.id
        WHERE bot_user_articles.sended is false

        """
        rows = await self._db.fetchall(query, as_dict=True)
        if rows is not None:
            return parse_obj_as(Tuple[UserEntry, ...], rows)

    async def mark_sended_entries(self, entry_id: int) -> None:
        query = f"""
        UPDATE bot_user_articles
        SET
            sended = true,
            sended_at = datetime('now')
        WHERE
            id = {self._paramstyle}
        """
        await self._db.execute(query, (entry_id,))

    async def exists_entry(self, url: str) -> bool:
        query = f"""
        SELECT 1
        FROM bot_articles
        WHERE url = {self._paramstyle}
        """
        row = await self._db.fetchone(query, (url,))
        return bool(row)

    async def get_entry_url(self, entry_id: int) -> Optional[str]:
        query = f"""
        SELECT url
        FROM bot_articles
        JOIN bot_user_articles on bot_articles.id = bot_user_articles.article_id
        WHERE
            bot_user_articles.id =  {self._paramstyle}
        """
        row = await self._db.fetchone(query, (entry_id,))
        if row:
            return row[0]  # type: ignore
