from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class User(BaseModel):
    id: int
    chat_id: int
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]
    active: bool
    register_at: datetime = Field(alias="register")


class PocketIntegraion(BaseModel):
    pocket_access_token: Optional[str]


class UserIntegration(PocketIntegraion):
    ...
