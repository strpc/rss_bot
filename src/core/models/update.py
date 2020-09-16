from src.core.utils import from_timestamp


class BaseMessage:
    def __init__(self, **kwargs):
        _message = kwargs.get('message')
        self.chat_id = _message.get('chat').get('id')
        self.first_name = _message.get('chat').get('first_name')
        self.last_name = _message.get('chat').get('last_name')
        self.username = _message.get('chat').get('username')
        self.date = from_timestamp(_message.get('date'))
        self.command = _message.get('text')
        self.type_message = False
        self.type_command = False


class BotCommand(BaseMessage):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type_command = True


class Message(BaseMessage):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type_message = True
