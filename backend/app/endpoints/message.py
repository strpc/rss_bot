from fastapi import APIRouter, Body, Response
from loguru import logger

from app.core.command.manager import CommandManager
from app.schemas.message import Message


router = APIRouter()


@router.post("/")
async def new_message(update: Message = Body(...)) -> Response:
    try:
        if not update.message.command:
            logger.warning("Unsupported update. body={}", update.dict(exclude_none=True))
            pass  # todo: обработать случай
            return Response(status_code=200)
        if update.message.command in vars(CommandManager) and not update.message.command.startswith(
            "_"
        ):
            attr = getattr(CommandManager, update.message.command)
            await attr(update)

    except Exception as error:
        logger.exception(error)
    finally:
        return Response(status_code=200)
