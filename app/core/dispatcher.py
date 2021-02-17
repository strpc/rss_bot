import logging
import re
from typing import Dict, Optional, Union

from pydantic import ValidationError

from app.core import schemas
from app.core.clients import Requests, Telegram
from app.core.db import SQLiteDB
from app.core.handlers.commands import CommandHandler
from app.core.schemas.input.base import TypeUpdate
from app.project.settings import DB_PATH, RSS_BOT_TOKEN


logger = logging.getLogger(__name__)
command_compile = re.compile(r"(^|\s)\/\b[^_][a-zA-Z_]+\b")


def identify_update(
    body: Dict,
) -> Optional[Union[schemas.Callback, schemas.Message, schemas.EditedMessage]]:
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
        logger.warning("%s\nUnsupported type update. Body:\n%s", error, body)
    return msg


def verify_update(
    update: Optional[Union[schemas.Callback, schemas.Message, schemas.EditedMessage]]
) -> bool:
    if (
        update is None
        or update.type_update is TypeUpdate.edited_message
        or update.type_update is TypeUpdate.message
        and update.message.text is None
    ):
        return False
    return True


def detect_command(update: schemas.Message) -> Optional[str]:
    text = update.message.text
    command = re.search(command_compile, text)[0][1:] if re.search(command_compile, text) else None
    logger.info("Detected command=%s", command)
    return command


def process(body: Dict):
    update = identify_update(body=body)

    if verify_update(update) is False:
        logger.warning("Unsupported update. body=%s", update)
        # пришло какое-то событие, которое мы не отслеживаем. todo: Сделать заглушку?
        return

    logger.debug("TypeUpdate=%s", update.type_update)

    if update.type_update is TypeUpdate.callback:
        # TODO: обрабатываем коллбек
        pass

    command = detect_command(update)
    telegram = Telegram(token=RSS_BOT_TOKEN, client=Requests())
    if command is not None and command in CommandHandler.__dict__.keys():
        with SQLiteDB(DB_PATH) as db:
            logger.debug("Inside to command handler...")
            handler = CommandHandler(database=db, telegram=telegram)
            getattr(handler, command)(update)
            return
    else:
        pass
        # !пришло обычное сообщение. нужно сделать заглушку.

    # todo:
    # !детектим команду
    # !если команда есть такая, то пускаем в оборот
    # !если команды такой нет, то идет пользователь нахер
