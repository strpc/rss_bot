from fastapi import APIRouter, Body, Depends, Response
from loguru import logger

from app.core.commands.command_abc import CommandServiceABC
from app.core.service_messages.deps import get_service_messages_service
from app.core.service_messages.models import ServiceMessage
from app.core.service_messages.service import ServiceMessagesService
from app.core.services_deps import get_command_service, get_current_user
from app.core.users.models import User
from app.custom_router import LoggingRoute
from app.schemas.message import Message


router = APIRouter(route_class=LoggingRoute)


@router.post("/")
async def new_message(
    update: Message = Body(...),
    command_service: CommandServiceABC = Depends(get_command_service),
    service_messages: ServiceMessagesService = Depends(get_service_messages_service),
    current_user: User = Depends(get_current_user),
) -> Response:
    try:
        if update.message.command is None or command_service is None:
            logger.warning("Неподдерживаемое событие. body={}", update.dict(exclude_none=True))
            await service_messages.send(
                current_user.chat_id,
                ServiceMessage.unsupported_update,
            )
            return Response(status_code=200)

        logger.debug("Handle command /{}", update.message.command)
        await command_service.handle(update)
    except Exception as error:
        logger.exception(error)
    finally:
        return Response(status_code=200)
