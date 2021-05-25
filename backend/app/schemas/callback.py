from typing import Optional

from app.schemas.enums import TypeUpdate
from app.schemas.message import MessageBody, User
from pydantic import BaseModel, Field


class Callback(BaseModel):
    id: str
    user: User = Field(..., alias="from")
    message: Optional[MessageBody] = None
    inline_message_id: Optional[str] = None
    data: Optional[str] = None
    type_update: TypeUpdate = TypeUpdate.callback
