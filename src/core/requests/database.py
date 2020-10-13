import logging
import sqlite3
import traceback
from abc import ABC, ABCMeta, abstractmethod
from datetime import datetime
from typing import Dict, List, Union, Tuple, Optional, Iterable

from src.project.settings import DB_PATH


logger = logging.getLogger(__name__)


class Obj(dict):
    @staticmethod
    def from_db(cursor: Iterable, row: Iterable) -> 'Obj':
        obj = Obj()
        for column, value in zip(cursor, row):
            obj[column] = value
        return obj

    def __getattr__(self, item):
        if item not in self.keys():
            raise AttributeError
        return self[item]


class Client(ABC):
    """Базовый класс коннектора к базе, от которого наследуемся"""

    @abstractmethod
    def __init__(self):
        self._conn = None
        self._cursor = None

    @staticmethod
    def dict_factory(cursor, row) -> Dict:
        """Делаем словарь из ответа базы {"поле": "значение"}"""
        data = {}
        for column, value in zip(cursor.description, row):
            data[column[0]] = value
        return data

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback_):
        self.disconnect()

    def connect(self):
        """Устанавливаем подключение к базе, делаем чтобы возвращался словарь"""
        if self._conn is None or self._cursor is None:
            self._conn = sqlite3.connect(DB_PATH)
            self._conn.row_factory = self.dict_factory
            self._cursor = self._conn.cursor()

    def disconnect(self):
        """Коммитим. Закрываем подключение к базе."""
        if self._conn is not None:
            self._conn.commit()
            self._conn.close()
            self._conn = None
            self._cursor = None

    @property
    def conn(self):
        """Получаем доступ ко всем методам"""
        if self._conn is None or self._cursor is None:
            self.connect()
        yield self._conn
        self.disconnect()

    def fetchall(self, query: str, values: Tuple = None) -> Optional[List[Dict]]:
        """Фетчолим запрос со значениями(или без)"""
        values = values or ()
        try:
            with self:
                self._cursor.execute(query, values)
                return self._cursor.fetchall() or None

        except Exception as error:
            logger.error(error)
            logger.error(traceback.format_exc())
            logger.info(query)

    def execute(self, query: str, values: Tuple = None) -> bool:
        """Экзекьютим запрос со значениями(или без)"""
        values = values or ()
        try:
            with self:
                self._conn.execute(query, values)
                return True

        except Exception as error:
            logger.error(error)
            logger.error(traceback.format_exc())
            logger.info(query)
            return False

    def executemany(self, query: str, values: List[Tuple]) -> bool:
        """Экзекьютим сразу несколько записей"""
        try:
            with self:
                self._conn.executemany(query, values)
                return True

        except Exception as error:
            logger.error(error)
            logger.error(traceback.format_exc())
            logger.info(query)
            return False


class MetaSingleton(ABCMeta):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Database(Client, metaclass=MetaSingleton):
    """Запросы в базу"""

    def __init__(self):
        super().__init__()
        self._conn = None
        self._cursor = None

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

    def init_user(self, chat_id: int) -> bool:
        """Инициализация пользователя(зареган ли он у нас уже)"""
        query = """SELECT 1 FROM bot_users WHERE chat_id = ? AND active = ?"""
        return bool(
            self.fetchall(query, (chat_id, True))
        )

    def disable_user(self, chat_id: int):
        """Пользователь отключился от бота"""
        query = """
        UPDATE bot_users
        SET active = ?
        WHERE chat_id = ?
        """
        self.execute(query, (
            False, chat_id
        ))

    def add_feed(self, values: List[Tuple]):
        """Добавляем новый RSS"""
        query = """
        INSERT INTO bot_users_rss (url, added, active, chat_id_id, chatid_url_hash)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT (chatid_url_hash) DO UPDATE SET active = true
        """
        self.executemany(query, values)

    def delete_feed(self, url: str, chat_id: int) -> bool:
        """Удаляем(отключаем) RSS пользователя"""
        if self.find_active_url(url, chat_id):
            query = """
            UPDATE bot_users_rss
            SET active = ?
            WHERE url = ?
            AND chat_id_id = ?
            """
            self.execute(query, (False, url, chat_id))
            return True
        return False

    def list_feed(self, chat_id: int) -> Optional[List[Dict]]:
        """Получаем список RSS, на который подписан пользователь"""
        query = """
        SELECT url
        FROM bot_users_rss
        WHERE chat_id_id = ?
        AND active = ?
        """
        return self.fetchall(query, (chat_id, True)) or None

    def find_active_url(self, url: str, chat_id: int) -> Optional[List[Dict]]:
        """Ищем активный RSS у пользователя"""
        query = """
        SELECT *
        FROM bot_users_rss
        WHERE url = ?
        AND chat_id_id = ?
        AND active = ?
        """
        result = self.fetchall(query, (url, chat_id, True))
        return result or None

    def get_active_feeds(self) -> Optional[List[Dict]]:
        """Получаем активные фиды активных юзеров"""
        query = """
        SELECT bot_users_rss.url, bot_users_rss.chat_id_id, bot_users_rss.chatid_url_hash
        FROM bot_users_rss
        JOIN bot_users ON bot_users_rss.chat_id_id = bot_users.chat_id
        AND bot_users.active = True
        WHERE bot_users_rss.active = True
        """
        return self.fetchall(query) or None

    def insert_articles(self, values: Union[List, Tuple]):
        """Сохраняем статьи"""
        query = """
        INSERT OR IGNORE INTO bot_article (
        url_article, title, text, added, sended, chatid_url_article_hash, rss_url_id, chat_id_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
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

    def mark_sended(self, values: Union[List, Tuple]):
        """Отмечаем, что статья отправлена пользователю"""
        query = """
        UPDATE bot_article
        SET sended = True
        WHERE url_article = ?
        AND chat_id_id = ?
        """
        self.executemany(query, values)
