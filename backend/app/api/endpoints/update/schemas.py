import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator

from app.api.endpoints.update.enums import ServiceIntegration, TypeChat, TypeEntity, TypeUpdate


COMMAND_COMPILE = re.compile(r"(^|\s)\/\b[^_][a-zA-Z_]+\b")


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
        command = COMMAND_COMPILE.search(text)
        return command[0][1:] if command else None


class Message(BaseModel):
    message: MessageBody
    update_id: int
    type_update: TypeUpdate = TypeUpdate.message


# class Button(BaseModel):
#     text: str
#     callback_data: Optional[str]


class CallbackIntegrationServicePayload(BaseModel):
    service: ServiceIntegration
    entry_id: int
    sended: bool


# class User(BaseModel):
#     id: int
#     is_bot: bool
#     first_name: Optional[str]
#     username: Optional[str]
#     language_code: Optional[str]


class BotInfo(BaseModel):
    id: int
    is_bot: bool
    first_name: Optional[str]
    username: Optional[str]


class ChatInfo(BaseModel):
    id: int
    first_name: Optional[str]
    username: Optional[str]
    type: Optional[str]


class Button(BaseModel):
    text: str
    callback_data: CallbackIntegrationServicePayload

    @validator("callback_data", pre=True, always=True)
    def validate_callback_data(cls, value: Any) -> Optional[CallbackIntegrationServicePayload]:
        if not isinstance(value, str):
            raise ValueError(f"value={value}")
        callback_data = json.loads(value)
        return CallbackIntegrationServicePayload(**callback_data)


class InlineKeyboard(BaseModel):
    inline_keyboard: List[List[Button]]


class CallbackMessage(BaseModel):
    message_id: int
    from_bot: BotInfo = Field(alias="from")
    chat: ChatInfo
    date: int
    text: str
    entities: List[Dict]
    reply_markup: InlineKeyboard


class CallbackQuery(BaseModel):
    id: int
    user: User = Field(alias="from")
    message: CallbackMessage
    chat_instance: str
    type_update: TypeUpdate = TypeUpdate.callback  # ??
    data: Optional[CallbackIntegrationServicePayload] = None

    @validator("data", pre=True, always=True)
    def validate_callback_data(cls, value: Any) -> Optional[CallbackIntegrationServicePayload]:
        if not isinstance(value, str):
            raise ValueError(f"value={value}")
        callback_data = json.loads(value)
        return CallbackIntegrationServicePayload(**callback_data)


class Callback(BaseModel):
    update_id: int
    callback_query: CallbackQuery
    type_update: TypeUpdate = TypeUpdate.callback


if __name__ == "__main__":
    update = Message(
        **{
            "message": {
                "chat": {
                    "first_name": "John",
                    "id": 888888889,
                    "last_name": "Smith",
                    "type": "private",
                    "username": "new_user",
                },
                "date": 1621453591,
                "entities": [{"length": 6, "offset": 0, "type": "bot_command"}],
                "from": {
                    "first_name": "Smith",
                    "id": 414077437,
                    "is_bot": False,
                    "language_code": "en",
                    "last_name": "John",
                    "username": "fuck you pay me",
                },
                "message_id": 9549,
                "text": "/start",
            },
            "update_id": 7476872561231412,
        }
    )
    print(update)
