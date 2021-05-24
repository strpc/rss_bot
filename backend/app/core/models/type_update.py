from enum import Enum


class TypeUpdate(str, Enum):
    command = "command"
    message = "message"
    callback = "callback"
    undefined = None
