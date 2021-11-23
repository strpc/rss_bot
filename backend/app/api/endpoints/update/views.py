from typing import Union

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, Response, status
from loguru import logger

from app.api.custom_router import LoggingRoute
from app.api.deps import get_command_service, get_current_user
from app.api.endpoints.update.schemas import Callback, Message
from app.containers import Container
from app.core.commands.command_abc import CommandServiceABC
from app.core.commands.dto import Update
from app.core.service_messages.models import InternalMessages
from app.core.service_messages.service import InternalMessagesService


router = APIRouter(route_class=LoggingRoute)


@router.post(
    "/",
    dependencies=[Depends(get_current_user)],
)
@inject
async def new_message(
    body: Union[Message, Callback] = Body(...),
    handle_service: CommandServiceABC = Depends(get_command_service),
    internal_messages: InternalMessagesService = Depends(
        Provide[Container.internal_messages_service],
    ),
) -> Response:
    update = Update.from_schema(body)

    try:
        if handle_service is None:
            logger.warning("Неподдерживаемое событие. body={}...", body.dict())
            await internal_messages.send(
                update.chat_id,
                InternalMessages.unsupported_update,
            )
            return Response(status_code=status.HTTP_200_OK)

        logger.debug("Handle update {}", update.to_dict())

        await handle_service.handle(update)
    except Exception as error:
        logger.debug("Handle update {}", update.to_dict())
        logger.exception(error)
    return Response(status_code=status.HTTP_200_OK)
