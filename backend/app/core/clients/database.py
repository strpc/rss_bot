import sqlite3
from types import TracebackType
from typing import Any, Dict, Iterable, List, Optional, Tuple, Type, Union

import aiosqlite
from loguru import logger


DictAny = Dict[str, Any]
TupleAny = Tuple[Any, ...]
ListDict = List[DictAny]
ListTuple = List[TupleAny]


class Database:
    def __init__(self, url: str):
        self._db = aiosqlite.connect(url)

    async def __aenter__(self) -> "Database":
        return await self.connect()

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        await self.disconnect()

    @staticmethod
    def _dict_factory(cursor: aiosqlite.Cursor, row: sqlite3.Row) -> Dict:
        """Делаем словарь из ответа базы {"поле": "значение"}"""
        data = {}
        for column, value in zip(cursor.description, row):
            data[column[0]] = value
        return data

    async def connect(self) -> "Database":
        await self._db
        return self

    async def disconnect(self) -> None:
        await self._db.close()

    async def fetchall(
        self,
        query: str,
        values: Optional[Iterable[Any]] = None,
        as_dict: bool = False,
    ) -> Optional[Union[DictAny, TupleAny]]:
        self._db.row_factory = self._dict_factory if as_dict else None  # type: ignore
        try:
            return await self._db.execute_fetchall(query, values) or None  # type: ignore
        finally:
            self._db.row_factory = None

    async def fetchone(
        self,
        query: str,
        values: Optional[Iterable[Any]] = None,
        as_dict: bool = False,
    ) -> Optional[Union[DictAny, Tuple[Any]]]:
        self._db.row_factory = self._dict_factory if as_dict else None  # type: ignore
        logger.debug("query\n{}\nvalues\n{}", query, values)
        try:
            cursor = await self._db.execute(query, values)
            row = await cursor.fetchone()
            await cursor.close()
            return row or None  # type: ignore
        finally:
            self._db.row_factory = None

    async def execute(
        self,
        query: str,
        values: Optional[Iterable[Any]] = None,
        autocommit: bool = True,
    ) -> None:
        await self._db.execute(query, values)
        if autocommit:
            await self._db.commit()

    async def executemany(
        self,
        query: str,
        values: Iterable[Iterable[Any]],
        autocommit: bool = True,
    ) -> None:
        await self._db.executemany(query, values)
        if autocommit:
            await self._db.commit()
