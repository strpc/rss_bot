from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class User(BaseModel):
    chat_id: int
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]
    active: bool = True
    registered: datetime = Field(alias="register", default_factory=datetime.now)
