from pydantic import BaseModel


class Button(BaseModel):
    title: str
    callback_data: str


class PocketButton(Button):
    title: str = "Save to Pocket"
