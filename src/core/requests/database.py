import logging
import sqlite3
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Union

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

    def __exit__(self, exc_type, exc_value, traceback):
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

    def fetchall(self, query: str) -> List[Dict]:
        try:
            with self as database:
                database.execute(query)
                return database.fetchall()

        except Exception as error:
            logger.error(error)
            logger.info(query)

    def execute(self, query: str) -> bool:
        try:
            with self as database:
                database.execute(query)
            return True

        except Exception as error:
            logger.error(error)
            logger.info(query)
            return False


class Database(Client):
    """Запросы в базу"""

    def __init__(self, chat_id: int):
        super().__init__()
        self.chat_id = chat_id
        self._conn = None

    def register_user(self, obj):
        """Регистрация пользователя"""
        query = """
        INSERT INTO bot_users (chat_id, first_name, last_name, username, register, active)
        VALUES (%s, '%s', '%s', '%s', '%s', %s)
        """
        self.execute((query % (
            obj.chat_id, obj.first_name, obj.last_name, obj.username, datetime.utcnow(), True
        )))

    def init_user(self) -> bool:
        """Инициализация пользователя(зареган ли он у нас уже)"""
        query = """SELECT 1 FROM bot_users WHERE chat_id = %s"""
        return bool(self.fetchall((query % self.chat_id)))

    def add_feed(self, url: Union[List, str]):
        pass

    def delete_feed(self) -> bool:
        pass

    def list_feed(self) -> List[str]:
        pass
