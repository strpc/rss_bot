from typing import NoReturn, Optional, Union

from dependency_injector.wiring import Provide, inject
from fastapi import Body, Depends, HTTPException, status
from loguru import logger

from app.api.endpoints.update.enums import TypeUpdate
from app.api.endpoints.update.schemas import Callback, Message
from app.containers import Container
from app.core.commands.add_feed.service import CommandAddFeedService
from app.core.commands.authorize_pocket.service import AuthorizePocketService
from app.core.commands.callbacks.service import CallbackService
from app.core.commands.delete_feed.service import CommandDeleteFeedService
from app.core.commands.help.service import CommandHelpService
from app.core.commands.integrations.service import CommandIntegrationsService
from app.core.commands.list_feed.service import CommandListFeedService
from app.core.commands.start.service import CommandStartService
from app.core.users.models import User
from app.core.users.service import UsersService


CommandsServicesType = Union[
    CommandIntegrationsService,
    AuthorizePocketService,
    CommandStartService,
    CommandHelpService,
    CommandAddFeedService,
    CommandListFeedService,
    CommandDeleteFeedService,
    CallbackService,
]


@inject
async def get_current_user(
    body: Union[Message, Callback] = Body(...),
    users_service: UsersService = Depends(Provide[Container.users_service]),
) -> Union[User, NoReturn]:
    user = await users_service.get_or_create(body)

    if user.is_blocked:
        logger.warning("Заблокированный юзер.")
        raise HTTPException(status_code=status.HTTP_200_OK)

    if not user.active:
        logger.info("Юзер найден, но не активен.")
        await users_service.activate_user(user.chat_id)
    return user


@inject
def get_command_service(
    body: Union[Message, Callback] = Body(...),
    container: Container = Depends(Provide[Container]),
) -> Optional[CommandsServicesType]:
    if body.type_update is TypeUpdate.callback:
        return container.callback_service()
    commands_map = {
        "start": container.command_start_service(),
        "help": container.command_help_service(),
        "add_feed": container.add_feed_service(),
        "list_feed": container.list_feed_service(),
        "delete_feed": container.delete_feed_service(),
        "integrations": container.integrations_service(),
        "authorize_pocket": container.authorize_pocket_service(),
        "unauthorize_pocket": container.authorize_pocket_service(),
    }
    return commands_map.get(body.message.command)  # type: ignore  # FIXME
