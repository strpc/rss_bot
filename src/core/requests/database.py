import logging
import sqlite3
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Union, Tuple, Optional
import traceback

from src.project.settings import DB_PATH


logger = logging.getLogger(__name__)


class Client(ABC):
    """Базовый класс коннектора к базе, от которого наследуемся"""

    @abstractmethod
    def __init__(self):
        self._conn = None

    @staticmethod
    def dict_factory(cursor, row) -> Dict:
        """Делаем словарь из ответа базы {"поле": "значение"}"""
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc_value, traceback_):
        self.disconnect()

    def connect(self):
        """Устанавливаем подключение к базе, делаем чтобы возвращался словарь"""
        self._conn = sqlite3.connect(DB_PATH)
        self._conn.row_factory = self.dict_factory
        return self._conn.cursor()

    def disconnect(self):
        """Коммитим. Закрываем подключение к базе."""
        self._conn.commit()
        self._conn.close()
        self._conn = None

    @property
    def conn(self):
        """Получаем доступ ко всем методам"""
        if self._conn is None:
            self.connect()
        return self._conn

    def fetchall(self, query: str, values: Tuple = None) -> List[Dict]:
        values = values or ()
        try:
            with self as database:
                database.execute(query, values)
                return database.fetchall()

        except Exception as error:
            logger.error(error)
            logger.error(traceback.format_exc())
            logger.info(query)

    def execute(self, query: str, values: Tuple = None) -> bool:
        values = values or ()
        try:
            with self as database:
                database.execute(query, values)
            return True

        except Exception as error:
            logger.error(error)
            logger.error(traceback.format_exc())
            logger.info(query)
            return False

    def executemany(self, query: str, values: List[Tuple]) -> bool:
        try:
            with self as database:
                database.executemany(query, values)
            return True

        except Exception as error:
            logger.error(error)
            logger.error(traceback.format_exc())
            logger.info(query)
            return False


class Database(Client):
    """Запросы в базу"""

    def __init__(self, chat_id: int = 0):
        super().__init__()
        self.chat_id = chat_id
        self._conn = None

    def register_user(self, obj):
        """Регистрация пользователя"""
        query = """
        INSERT INTO bot_users (chat_id, first_name, last_name, username, register, active)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT (chat_id) DO UPDATE SET active = true
        """
        self.execute(query, (
            obj.chat_id, obj.first_name, obj.last_name, obj.username, datetime.utcnow(), True,
        )
                     )

    def init_user(self) -> bool:
        """Инициализация пользователя(зареган ли он у нас уже)"""
        query = """SELECT 1 FROM bot_users WHERE chat_id = ? AND active = ?"""
        return bool(
            self.fetchall(query, (self.chat_id, True))
        )

    def disable_user(self):
        """Пользователь отключился от бота"""
        query = """
        UPDATE bot_users
        SET active = ?
        WHERE chat_id = ?
        """
        self.execute(query, (
            False, self.chat_id
        ))

    def add_feed(self, values: Union[List, Tuple]):
        query = """
        INSERT INTO bot_users_rss (url, added, active, chat_id_id, chatid_url_hash)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT (chatid_url_hash) DO UPDATE SET active = true
        """
        self.executemany(query, values)

    def delete_feed(self, url: str) -> bool:
        if self.find_active_url(url):
            query = """
            UPDATE bot_users_rss
            SET active = ?
            WHERE url = ?
            AND chat_id_id = ?
            """
            self.execute(query, (False, url, self.chat_id))
            return True
        return False

    def list_feed(self) -> List[Dict]:
        query = """
        SELECT url 
        FROM bot_users_rss
        WHERE chat_id_id = ?
        AND active = ?
        """
        return self.fetchall(query, (self.chat_id, True))

    def find_active_url(self, url: str) -> Optional[List[Dict]]:
        query = """
        SELECT *
        FROM bot_users_rss
        WHERE url = ?
        AND chat_id_id = ?
        AND active = ?
        """
        result = self.fetchall(query, (url, self.chat_id, True))
        return result or None

    def get_active_feeds(self) -> Optional[List[Dict]]:
        """Получаем активные фиды активных юзеров"""
        query = """
        SELECT bot_users_rss.url, bot_users_rss.chat_id_id
        FROM bot_users_rss
        JOIN bot_users ON bot_users_rss.chat_id_id = bot_users.chat_id 
        AND bot_users.active = True
        WHERE bot_users_rss.active = True
        """
        return self.fetchall(query) or None

    def insert_articles(self, values: Union[List, Tuple]):
        """Сохраняем статьи"""
        query = """
        INSERT INTO bot_article (
        url_article, title, text, added, sended, chatid_url_article_hash, chat_id_id 
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT (chatid_url_article_hash) DO UPDATE SET sended = false
        """
        self.executemany(query, values)

    def get_ready_articles(self) -> Optional[List[Dict]]:
        """Получаем готовые к отправке статьи активных юзеров"""
        query = """
        SELECT url_article, title, text, chat_id_id
        FROM bot_article
        JOIN bot_users ON bot_article.chat_id_id = bot_users.chat_id 
        AND bot_users.active = True
        WHERE bot_article.sended = False
        """
        return self.fetchall(query) or None
