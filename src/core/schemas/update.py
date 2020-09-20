from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Union
import re

# from src.core.utils import from_timestamp
from src.core.requests.database import Database
from src.core.requests.api import Request
from src.core.schemas.rss import ListUrls


command_compile = re.compile(r'(^|\s)\/\b[a-zA-Z_]+\b')


class TypeUpdate(str, Enum):
    command = 'command'
    message = 'message'
    undefined = None


class BaseMessage(ABC):
    @abstractmethod
    def __init__(self, **kwargs):
        _message = kwargs.get('message')
        self.chat_id = _message.get('chat').get('id')
        self.first_name = _message.get('chat').get('first_name')
        self.last_name = _message.get('chat').get('last_name')
        self.username = _message.get('chat').get('username')
        # self.date = from_timestamp(_message.get('date'))
        self.text = ''
        self.command = ''
        self.type_update = TypeUpdate.undefined.value
        self.new_user = False

    def _init_user(self) -> bool:
        self.new_user = False if self.database.init_user() else True
        return self.new_user

    @property
    def database(self):
        return Database(chat_id=self.chat_id)

    @property
    def request(self):
        return Request(chat_id=self.chat_id)

    def send_message(
            self, message_: str,
            parse_mode: str = None,
            disable_web_page_preview: bool = False
    ):
        self.request.send_message(message_, parse_mode, disable_web_page_preview)

    def add_feed(self, urls: Union[ListUrls, List, str]):
        self.database.add_feed(urls)

    def list_feed(self):
        return self.database.list_feed()

    def delete_feed(self, url: str):
        return self.database.delete_feed(url)


class BotCommand(BaseMessage):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        _text = kwargs.get('message').get('text')
        self.command = re.search(command_compile, _text)[0] \
            if re.search(command_compile, _text) else None
        self.text = re.sub(command_compile, '', _text)
        self.command_raw = self.command[1:] if self.command else None
        self.type_update = TypeUpdate.command.value

    def register_user(self):
        self.database.register_user(self)

    def init_user(self):
        return self._init_user()

    def __repr__(self) -> str:
        return f'Command: {self.command}. @{self.username}, {self.chat_id}'


class Message(BaseMessage):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = kwargs.get('message').get('text')
        self.type_update = TypeUpdate.message.value

    def __repr__(self):
        return f'Message: {self.text}. @{self.username}, {self.chat_id}'


class FromDB(BaseMessage):
    def __init__(self, chat_id: int):
        self.chat_id = chat_id
