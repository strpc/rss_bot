from abc import ABC
from enum import Enum

from src.core.utils import from_timestamp
from src.core.requests.database import Database
from src.core.requests.api import Request


class TypeUpdate(str, Enum):
    command = 'command'
    message = 'message'
    undefined = None


class BaseMessage(ABC):
    def __init__(self, **kwargs):
        _message = kwargs.get('message')
        self.chat_id = _message.get('chat').get('id')
        self.first_name = _message.get('chat').get('first_name')
        self.last_name = _message.get('chat').get('last_name')
        self.username = _message.get('chat').get('username')
        self.date = from_timestamp(_message.get('date'))
        self.text = ''
        self.command = ''
        self.type_update = TypeUpdate.undefined.name
        self.new_user = False
        self.init_user()

    def init_user(self):
        # if user is None:
        self.new_user = True

    @property
    def database(self):
        return Database()

    @property
    def request(self):
        return Request()


class BotCommand(BaseMessage):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.command = kwargs.get('message').get('text')
        self.type_update = TypeUpdate.command.name
        # if self.new_user:
        self.register_user()

        # если не новый и команда /start - raise ошибка

    def register_user(self):
        # if user not in database
        pass

    def __repr__(self):
        return f'Command: {self.command}. {self.username}, {self.chat_id}, {self.date}'


class Message(BaseMessage):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = kwargs.get('message').get('text')
        self.type_update = TypeUpdate.message.name

    def __repr__(self):
        return f'Message: {self.text}. {self.username}, {self.chat_id}, {self.date}'

