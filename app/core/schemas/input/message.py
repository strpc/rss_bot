from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.core.schemas.input.base import Chat, TypeEntity, TypeUpdate, User


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
    user: User = Field(..., alias='from')
    message_id: int
    text: Optional[str] = None


class Message(BaseModel):
    message: MessageBody
    update_id: int
    type_update: TypeUpdate = TypeUpdate.message
