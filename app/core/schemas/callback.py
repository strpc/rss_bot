from typing import Optional

from pydantic import BaseModel, Field

from app.core.schemas.message import MessageBody, User


class Callback(BaseModel):
    id: str
    user: User = Field(..., alias='from')
    message: Optional[MessageBody] = None
    inline_message_id: Optional[str] = None
    data: Optional[str] = None
