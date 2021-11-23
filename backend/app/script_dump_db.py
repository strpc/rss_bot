import asyncio
import base64
import os
import typing as t
from datetime import datetime
from types import TracebackType

from loguru import logger
from pydantic import BaseModel, Field, parse_obj_as, validator

from app.clients.database import Database


CURRENT_DIR = os.path.abspath(os.path.dirname(__name__))
OLD_DB_PATH = os.path.join(CURRENT_DIR, "db_format/db_v1.sqlite3")
NEW_DB_PATH = os.path.join(CURRENT_DIR, "db_format/db_v2.sqlite3")


class User(BaseModel):
    chat_id: int
    first_name: t.Optional[str]
    last_name: t.Optional[str]
    username: t.Optional[str]
    register_at: datetime = Field(alias="register")
    active: bool
    is_blocked: t.Optional[bool] = False


class UserRSS(BaseModel):
    url: str
    added: datetime
    active: bool
    chat_id: int


class Article(BaseModel):
    url: str
    text: str
    added: datetime
    rss_url: str
    title: str

    @validator("rss_url", pre=True, always=True)
    def validate_rss_id(cls, value: str) -> str:
        return base64.b64decode(value.encode()).decode()[:-9]


class UserArticle(Article):
    chat_id: int
    sended: bool
    sended_at: datetime


class Nasos:
    def __init__(self) -> None:
        self.old_db = Database(OLD_DB_PATH)
        self.new_db = Database(NEW_DB_PATH)

    async def __aenter__(self) -> None:
        await self.old_db.__aenter__()
        await self.new_db.__aenter__()

    async def __aexit__(
        self,
        exc_type: t.Optional[t.Type[BaseException]],
        exc_value: t.Optional[BaseException],
        traceback: t.Optional[TracebackType],
    ) -> None:
        await self.old_db.__aexit__(exc_type, exc_value, traceback)
        await self.new_db.__aexit__(exc_type, exc_value, traceback)

    async def select_users(self) -> t.Optional[t.Tuple[User, ...]]:
        query = "SELECT chat_id, first_name, last_name, username, register, active FROM bot_users"
        rows = await self.old_db.fetchall(query, as_dict=True)
        return parse_obj_as(t.Tuple[User, ...], rows)

    async def insert_users(self, users: t.Tuple[User, ...]) -> None:
        query = """
        INSERT INTO bot_users
        (chat_id, first_name, last_name, username, register, active, is_blocked)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        await self.new_db.executemany(
            query,
            [tuple(user.dict(by_alias=True).values()) for user in users],
        )

    async def get_rss(self) -> t.Optional[t.List[t.Tuple[str, ...]]]:
        query = "SELECT url FROM bot_users_rss"
        rows = await self.old_db.fetchall(query)
        if rows is not None:
            return rows  # type: ignore

    async def insert_rss(self, rss: t.List[t.Tuple[str, ...]]) -> None:
        query = "INSERT INTO bot_rss (url) VALUES (?)"
        await self.new_db.executemany(query, rss)

    async def get_users_rss(self) -> t.Optional[t.Tuple[UserRSS, ...]]:
        query = """
        SELECT
            url, added, active, chat_id_id as chat_id
        FROM bot_users_rss
        """
        rows = await self.old_db.fetchall(query, as_dict=True)
        if rows is not None:
            return parse_obj_as(t.Tuple[UserRSS, ...], rows)

    async def insert_users_rss(self, users_rss: t.Tuple[UserRSS, ...]) -> None:
        query = """
        INSERT INTO bot_rss_user (rss_id, user_id, active, added, updated)
        VALUES (
        (SELECT id FROM bot_rss WHERE url = ?),
        (SELECT id FROM bot_users WHERE chat_id = ?),
        ?,
        ?,
        ?
        )
        """
        values = []
        for user_rss in users_rss:
            values.append(
                (
                    user_rss.url,
                    user_rss.chat_id,
                    user_rss.active,
                    user_rss.added,
                    user_rss.added,
                ),
            )
        await self.new_db.executemany(query, values)

    async def get_articles(self) -> t.Optional[t.Tuple[Article, ...]]:
        query = """
        SELECT url_article as url, text, added, rss_url_id as rss_url, title
        FROM bot_article"""
        rows = await self.old_db.fetchall(query, as_dict=True)
        if rows is not None:
            return parse_obj_as(t.Tuple[Article, ...], rows)

    async def insert_articles(self, articles: t.Tuple[Article, ...]) -> None:
        query = """
        INSERT INTO bot_articles (url, text, added, rss_id, title)
        VALUES (
        ?,
        ?,
        ?,
        (SELECT id FROM bot_rss WHERE url = ?),
        ?
        )
        """
        await self.new_db.executemany(
            query,
            [tuple(article.dict(by_alias=True).values()) for article in articles],
        )

    async def get_users_articles(self) -> t.Optional[t.Tuple[UserArticle, ...]]:
        query = """
        SELECT
            url_article as url,
            text,
            added,
            rss_url_id as rss_url,
            title,
            chat_id_id as chat_id,
            sended,
            added as sended_at
        FROM bot_article
        """
        rows = await self.old_db.fetchall(query, as_dict=True)
        if rows is not None:
            return parse_obj_as(t.Tuple[UserArticle, ...], rows)

    async def insert_users_articles(self, users_articles: t.Tuple[UserArticle, ...]) -> None:
        query = """
        INSERT INTO bot_user_articles (added, sended_at, sended, article_id, user_id)
        VALUES (
        ?,
        ?,
        ?,
        (SELECT id FROM bot_articles WHERE url = ?),
        (SELECT id FROM bot_users WHERE chat_id = ?)
        )
        """
        await self.new_db.executemany(
            query,
            [
                (
                    user_article.added,
                    user_article.added,
                    user_article.sended,
                    user_article.url,
                    user_article.chat_id,
                )
                for user_article in users_articles
            ],
        )


async def main() -> None:
    nasos = Nasos()
    async with nasos:
        users = await nasos.select_users()
        if users is None:
            logger.error("Юзеры не найдены.")
            exit(10)
        await nasos.insert_users(users)
        rss = await nasos.get_rss()
        if rss is None:
            logger.error("RSS не найдены.")
            exit(10)
        await nasos.insert_rss(rss)
        users_rss = await nasos.get_users_rss()
        if users_rss is None:
            logger.error("Не найдены подписки юзеров.")
            exit(10)
        await nasos.insert_users_rss(users_rss)
        articles = await nasos.get_articles()
        if articles is None:
            logger.error("Статьи не найдены.")
            exit(10)
        await nasos.insert_articles(articles)
        users_articles = await nasos.get_users_articles()
        if users_articles is None:
            logger.error("Не найдены статьи пользователей.")
            exit(10)
        await nasos.insert_users_articles(users_articles)


if __name__ == "__main__":
    asyncio.run(main())
