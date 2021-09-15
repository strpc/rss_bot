from typing import Union

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, Response, status
from loguru import logger

from app.api.deps import get_command_service, get_current_user
from app.api.schemas.callback import Callback
from app.api.schemas.enums import TypeUpdate
from app.api.schemas.message import Message
from app.containers import Container
from app.core.commands.command_abc import CommandServiceABC
from app.core.service_messages.models import InternalMessages
from app.core.service_messages.service import InternalMessagesService
from app.core.users.models import User
from app.custom_router import LoggingRoute
from app.reporters_errors import get_telegram_reporter


router = APIRouter(route_class=LoggingRoute)
telegram_reporter = get_telegram_reporter()


@router.post("/")
@telegram_reporter(as_attached=True)
@inject
async def new_message(
    update: Union[Message, Callback] = Body(...),
    handle_service: CommandServiceABC = Depends(get_command_service),
    internal_messages: InternalMessagesService = Depends(
        Provide[Container.internal_messages_service],
    ),
    current_user: User = Depends(get_current_user),
) -> Response:
    try:
        if (
            update.type_update is TypeUpdate.message
            and update.message.command is None
            or handle_service is None
        ):
            logger.warning("Неподдерживаемое событие. body={}...", update.dict(exclude_none=True))
            await internal_messages.send(
                current_user.chat_id,
                InternalMessages.unsupported_update,
            )
            return Response(status_code=status.HTTP_200_OK)

        if update.type_update is TypeUpdate.message:
            logger.debug("Handle command /{}...", update.message.command)
        else:
            logger.debug("Handle {}", update.type_update)
        await handle_service.handle(update)
    except Exception as error:
        logger.exception(error)
    return Response(status_code=status.HTTP_200_OK)
