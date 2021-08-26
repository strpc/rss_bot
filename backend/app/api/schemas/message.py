import re
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator

from app.api.schemas.enums import TypeChat, TypeEntity, TypeUpdate


command_compile = re.compile(r"(^|\s)\/\b[^_][a-zA-Z_]+\b")


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


class MessageEntity(BaseModel):
    length: int
    offset: int
    type: TypeEntity
    url: Optional[str] = None
    user: Optional[str] = None
    language: Optional[str] = None


class MessageBody(BaseModel):
    chat: Chat
    date: datetime
    entities: Optional[List[MessageEntity]] = None
    user: User = Field(..., alias="from")
    message_id: int
    text: str
    command: Optional[str] = None

    @validator("command", always=True)
    def validate_command(cls, v: None, values: Dict) -> Optional[str]:
        text = values.get("text")
        if text is None:
            return v

        command = re.search(command_compile, text)
        return command[0][1:] if command else None


class Message(BaseModel):
    message: MessageBody
    update_id: int
    type_update: TypeUpdate = TypeUpdate.message


class Button(BaseModel):
    text: str
    callback_data: Optional[str]
