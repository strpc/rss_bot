from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union


class IDatabase(ABC):
    @abstractmethod
    def register_user(self, obj: Tuple[Any]): ...

    @abstractmethod
    def init_user(self, chat_id: int) -> bool: ...

    @abstractmethod
    def disable_user(self, chat_id: int): ...

    @abstractmethod
    def add_feed(self, values: List[Tuple]): ...

    @abstractmethod
    def delete_feed(self, url: str, chat_id: int) -> bool: ...

    @abstractmethod
    def list_feed(self, chat_id: int) -> Optional[List[Dict]]: ...

    @abstractmethod
    def find_active_url(self, url: str, chat_id: int) -> Optional[List[Dict]]: ...

    @abstractmethod
    def get_active_feeds(self) -> Optional[List[Dict]]: ...

    @abstractmethod
    def insert_articles(self, values: Union[List, Tuple]): ...

    @abstractmethod
    def get_ready_articles(self) -> Optional[List[Dict]]: ...

    @abstractmethod
    def mark_sended(self, values: Union[List, Tuple]): ...
