from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class User(BaseModel):
    id: Optional[int]
    chat_id: int
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]
    register_at: datetime = Field(alias="register", default_factory=datetime.now)
    active: bool = True
    is_blocked: bool = False


class PocketIntegraion(BaseModel):
    pocket_access_token: Optional[str]


class UserIntegration(PocketIntegraion):
    ...
