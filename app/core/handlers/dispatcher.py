import logging
import re
from typing import Dict, Optional, Union

from pydantic import ValidationError

from app.core import models
from app.core import schemas
from app.core.schemas.input.base import TypeUpdate

# from app.core.handlers.commands import CommandHandler
# from app.core.schemas.update import BaseMessage, BotCommand, TypeUpdate
# from app.core.factory import Factory


logger = logging.getLogger(__name__)
command_compile = re.compile(r'(^|\s)\/\b[a-zA-Z_]+\b')  # ! возможно нужно брать -1 элемент


def identify_update(body: Dict) -> Optional[
    Union[schemas.Callback, schemas.Message, schemas.EditedMessage]
]:
    msg = None
    try:
        msg = schemas.Message.parse_obj(body)
        return msg
    except ValidationError:
        pass

    try:
        msg = schemas.Callback.parse_obj(body)
        return msg
    except ValidationError:
        pass

    try:
        msg = schemas.EditedMessage.parse_obj(body)
    except ValidationError as error:
        logger.warning('%s\nUnsupported type update. Body:\n%s', error, body)
    return msg


def verify_update(
        update: Optional[
            Union[schemas.Callback, schemas.Message, schemas.EditedMessage]
        ]) -> bool:
    if (
            update is None
            or update.type_update is TypeUpdate.edited_message
            or update.type_update is TypeUpdate.message and update.message.text is None
    ):
        return False
    return True


def detect_command(update: schemas.Message) -> Optional[str]:
    text = update.message.text
    command = re.search(command_compile, text)[0] if re.search(command_compile, text) else None
    return command


def process(body: Dict):
    update = identify_update(body=body)

    if verify_update(update) is False:
        logger.warning('Unsupported update. body=%s', update)
        # пришло какое-то событие, которое мы не отслеживаем. todo: Сделать заглушку?
        return

    logger.debug(update.type_update)

    if True:
        pass
        # result = models.Message(
        #     chat_id=update.message.chat.id,
        #     first_name=update.message.user.first_name,
        #     last_name=update.message.user.last_name,
        #     username=update.message.user.username,
        #     text=update.message.text,
        # )
        # todo: обработка сообщения
    else:
        pass
        # result = models.Callback()  # TODO IN PROGRESS: обработка коллбека

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
