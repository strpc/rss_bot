from typing import Dict

from src.core.schemas.update import Message, BotCommand


class ObjectFactory:
    def __init__(self, list_obj: Dict):
        self._builders = list_obj

    def register_message(self, message: Dict):
        type_msg = 'message'
        entitles = message.get('message').get('entities')
        if entitles:
            for entitle in entitles:
                for k, v in entitle.items():
                    if v in self._builders.keys():
                        type_msg = v

        obj = self._builders.get(type_msg)
        return obj(**message)


type_obj = {
    'bot_command': BotCommand,
    'message': Message,
}


Factory = ObjectFactory(type_obj)
