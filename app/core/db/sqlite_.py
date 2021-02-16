import logging
import sqlite3
import traceback
from typing import Dict, List, Optional, Tuple, Union

from app.core.db.base import IDatabase


logger = logging.getLogger(__name__)


class SQLiteClient:
    """Базовый класс коннектора к базе, от которого наследуемся"""

    def __init__(self, db_path: str):
        self._db_path = db_path
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
            self._conn = sqlite3.connect(self._db_path)
            self._conn.row_factory = self.dict_factory
            self._cursor = self._conn.cursor()

    def disconnect(self):
        """Коммитим. Закрываем подключение к базе."""
        if self._conn is not None:
            self._conn.commit()
            self._conn.close()
            self._conn = None
            self._cursor = None

    def fetchall(self, query: str, values: Optional[Tuple] = None) -> Optional[List[Dict]]:
        """Фетчолим запрос со значениями(или без)"""
        values = values or ()
        try:
            self._cursor.execute(query, values)
            return self._cursor.fetchall() or None
        except Exception as error:
            logger.error(error)
            logger.error(traceback.format_exc())
            logger.warning(query)

    def execute(self, query: str, values: Optional[Tuple] = None) -> bool:
        """Экзекьютим запрос со значениями(или без)"""
        values = values or ()
        try:
            self._conn.execute(query, values)
            return True
        except Exception as error:
            logger.error(error)
            logger.error(traceback.format_exc())
            logger.warning(query)
            return False

    def executemany(self, query: str, values: List[Tuple]) -> bool:
        """Экзекьютим сразу несколько записей"""
        try:
            self._conn.executemany(query, values)
            return True
        except Exception as error:
            logger.error(error)
            logger.error(traceback.format_exc())
            logger.warning(query)
            return False


class SQLiteDB(IDatabase, SQLiteClient):
    """Класс для работы с SQLite"""

    def registered_user(self, chat_id: int) -> bool:
        """
        Инициализация пользователя: зареган ли он у нас.
        Args:
            chat_id(int): chat_id пользователя

        Returns:
            bool: True, если да, False - если нет.
        """
        query = """SELECT 1 FROM bot_users WHERE chat_id = ? AND active = ?"""
        return bool(self.fetchall(query, (chat_id, True)))

    """Запросы в базу"""

    def register_user(self, chat_id: int, first_name: str, last_name: str, username: str):
        """
        Регистрация пользователя. Если такой уже есть, но выключен - активация.
        Args:
            chat_id(int): chat_id с юзером.
            first_name(str): Имя пользователя.
            last_name(str): Фамилия пользователя.
            username(str): Никнейм пользователя
        """
        query = """
        INSERT INTO bot_users (chat_id, first_name, last_name, username, register, active)
        VALUES (?, ?, ?, ?, true, datetime('now'))
        ON CONFLICT (chat_id) DO UPDATE SET active = true
        """
        self.execute(query, (chat_id, first_name, last_name, username))

    def get_service_message(self, title: str) -> Dict:
        """
        Получение сервисных сообщений из базы.
        Args:
            title(str): Заголовок, для которого нужно получить сообщение.

        Returns:
            dict: Словарь с найденным сообщением.
        """  # TODO: дополнить примером
        query = ""
        # self.fetchall('')
        print(self.fetchall, title, query)
        return {"message": "Добро пожаловаться"}

    def disable_user(self, chat_id: int):
        """Пользователь отключился от бота"""
        query = """
        UPDATE bot_users
        SET active = ?
        WHERE chat_id = ?
        """
        self.execute(query, (False, chat_id))

    def add_feed(self, *, url: str, chat_id: int, hash_url: str):
        """
        Добавляем новый RSS пользователя.
        Args:
            url(str): url фида.
            chat_id: chat_id с юзером.
            hash_url(str): хеш url+chat_id
        """
        query = """
        INSERT INTO bot_users_rss (url, chat_id_id, chatid_url_hash, added, active)
        VALUES (?, ?, ?, datetime('now'), true)
        ON CONFLICT (chatid_url_hash) DO UPDATE SET active = true
        """
        self.execute(query, (url, chat_id, hash_url))

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
