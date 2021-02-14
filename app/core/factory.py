import logging
import traceback
from typing import Dict

from pydantic import ValidationError

from app.core.updates import Message, Callback
# from app.core.schemas.update import Message, BotCommand


logger = logging.getLogger(__name__)


class ObjectFactory:
    def __init__(self, list_obj: Dict):
        self._builders = list_obj

    def register_message(self, update: Dict):
        msg = None
        try:
            msg = Message.parse_obj(update)
        except ValidationError:
            msg = Callback.parse_obj(update)
        except Exception as error:
            logger.error('%s, %s\n\n%s', error, update, traceback.format_exc())
        return msg
        # obj = self._builders.get(type_msg)
        # return obj(**update)


# type_obj = {
#     'bot_command': BotCommand,
#     'code': BotCommand,
#     'message': Message,
# }


# Factory = ObjectFactory(type_obj)
Factory = ObjectFactory({})
