from enum import Enum
from typing import Optional

from pydantic import BaseModel


class TypeUpdate(str, Enum):
    message = "message"
    callback = "callback"
    edited_message = "edited_message"


class TypeChat(str, Enum):
    private = "private"
    group = "group"
    supergroup = "supergroup"
    channel = "channel"


class TypeEntity(str, Enum):
    url = "url"
    bot_command = "bot_command"
    code = "code"
    mention = "mention"
    hashtag = "hashtag"
    cashtag = "cashtag"
    email = "email"
    phone_number = "phone_number"
    bold = "bold"
    italic = "italic"
    underline = "underline"
    strikethrough = "strikethrough"
    pre = "pre"
    text_link = "text_link"
    text_mention = "text_mention"


class User(BaseModel):
    id: int
    is_bot: bool
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None


class Chat(BaseModel):
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    type: TypeChat
    username: Optional[str] = None
