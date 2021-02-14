from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class TypeChat(str, Enum):
    private = 'private'
    group = 'group'
    supergroup = 'supergroup'
    channel = 'channel'


class TypeEntity(str, Enum):
    url = 'url'
    bot_command = 'bot_command'
    code = 'code'
    mention = 'mention'
    hashtag = 'hashtag'
    cashtag = 'cashtag'
    email = 'email'
    phone_number = 'phone_number'
    bold = 'bold'
    italic = 'italic'
    underline = 'underline'
    strikethrough = 'strikethrough'
    pre = 'pre'
    text_link = 'text_link'
    text_mention = 'text_mention'


class User(BaseModel):
    id: int
    is_bot: bool
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None


class MessageEntity(BaseModel):
    length: int
    offset: int
    type: TypeEntity
    url: Optional[str] = None
    user: Optional[str] = None
    language: Optional[str] = None


class Chat(BaseModel):
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    type: TypeChat
    username: Optional[str] = None


class MessageBody(BaseModel):
    chat: Chat
    date: int
    entities: Optional[List[MessageEntity]] = None
    user: User = Field(..., alias='from')
    message_id: int
    text: Optional[str] = None


class Message(BaseModel):
    message: MessageBody
    update_id: int
