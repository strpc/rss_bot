import logging
import traceback
from typing import Dict, Union, Optional, Type

from pydantic import ValidationError

from app.core import schemas
from app.core import models
# from app.core.handlers.commands import CommandHandler
# from app.core.schemas.update import BaseMessage, BotCommand, TypeUpdate
# from app.core.factory import Factory


logger = logging.getLogger(__name__)


def detect_update(
        *,
        body: Dict,
        message: Type[schemas.Message],
        callback: Type[schemas.Callback],
) -> Optional[Union[schemas.Callback, schemas.Message]]:
    msg = None
    try:
        msg = message.parse_obj(body)
    except ValidationError:
        msg = callback.parse_obj(body)
    except Exception as error:
        logger.error('%s, %s\n\n%s', error, body, traceback.format_exc())
    return msg


def process(body: Dict):
    update = detect_update(body=body, message=schemas.Message, callback=schemas.Callback)

    if update is None:
        # пришло какое-то событие, которое мы не отслеживаем.
        return

    if isinstance(update, schemas.Message):
        result = models.Message(
            chat_id=update.message.chat.id,
            first_name=update.message.user.first_name,
            last_name=update.message.user.last_name,
            username=update.message.user.username,
            text=update.message.text,
        )
        # todo: обработка сообщения
    else:
        result = models.Callback()  # TODO IN PROGRESS: обработка коллбека

    # if (message.type_update == TypeUpdate.command.value and
    #         message.command_raw in CommandHandler.__dict__.keys()):
    #     getattr(CommandHandler, message.command_raw)(message)
    #
    # elif (
    #         message.type_update == TypeUpdate.message.value
    #         or message.type_update == TypeUpdate.command.value
    # ):
    #     pass  # пришло обычное сообщение. нужно сделать заглушку.
    #     print('обычное сообщение')
    #     print(message.text)
