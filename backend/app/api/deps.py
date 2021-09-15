from typing import NoReturn, Optional, Union

from dependency_injector.wiring import Provide, inject
from fastapi import Body, Depends, HTTPException, status
from loguru import logger

from app.api.schemas.callback import Callback
from app.api.schemas.enums import TypeUpdate
from app.api.schemas.message import Message
from app.containers import Container
from app.core.callbacks.service import CallbackService
from app.core.commands.add_feed.service import CommandAddFeedService
from app.core.commands.authorize.service import AuthorizeService
from app.core.commands.authorize_pocket.service import AuthorizePocketService
from app.core.commands.delete_feed.service import CommandDeleteFeedService
from app.core.commands.list_feed.service import CommandListFeedService
from app.core.commands.start.service import CommandStartService
from app.core.users.models import User
from app.core.users.service import UsersService


CommandsServicesType = Union[
    AuthorizeService,
    AuthorizePocketService,
    CommandStartService,
    CommandAddFeedService,
    CommandListFeedService,
    CommandDeleteFeedService,
    CallbackService,
]


@inject
async def get_current_user(
    users_service: UsersService = Depends(Provide[Container.users_service]),
    update: Union[Message, Callback] = Body(...),
) -> Union[User, NoReturn]:
    user = await users_service.get_or_create(update)

    if user.is_blocked:
        logger.warning("Заблокированный юзер.")
        raise HTTPException(status_code=status.HTTP_200_OK)

    if not user.active:
        logger.info("Юзер найден, но не активен.")
        await users_service.activate_user(user.chat_id)
    return user


@inject
def get_command_service(
    update: Union[Message, Callback] = Body(...),
    container: Container = Depends(Provide[Container]),
) -> Optional[CommandsServicesType]:
    if update.type_update is TypeUpdate.callback:
        return container.callback_service()
    commands_map = {
        "start": container.command_start_service(),
        "add_feed": container.add_feed_service(),
        "list_feed": container.list_feed_service(),
        "delete_feed": container.delete_feed_service(),
        "authorize": container.authorize_service(),
        "authorize_pocket": container.authorize_pocket_service(),
        "unauthorize_pocket": container.authorize_pocket_service(),
    }
    return commands_map.get(update.message.command)  # type: ignore  # FIXME
