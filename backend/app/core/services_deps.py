from typing import Optional, Union

from fastapi import Body, Depends
from loguru import logger

from app.core.callbacks.deps import get_callback_service
from app.core.callbacks.service import CallbackService
from app.core.commands.add_feed.deps import get_command_add_feed_service
from app.core.commands.add_feed.service import CommandAddFeedService
from app.core.commands.authorize.deps import get_command_authorize_service
from app.core.commands.authorize.service import AuthorizeService
from app.core.commands.authorize_pocket.deps import (
    get_authorize_pocket_service,
    get_unauthorize_pocket_service,
)
from app.core.commands.authorize_pocket.service import (
    AuthorizePocketService,
    UnAuthorizePocketService,
)
from app.core.commands.delete_feed.deps import get_command_delete_feed_service
from app.core.commands.delete_feed.service import CommandDeleteFeedService
from app.core.commands.list_feed.deps import get_command_list_feed_service
from app.core.commands.list_feed.service import CommandListFeedService
from app.core.commands.start.deps import get_command_start_service
from app.core.commands.start.service import CommandStartService
from app.core.users.deps import get_users_service
from app.core.users.models import User
from app.core.users.service import UsersService
from app.schemas.callback import Callback
from app.schemas.enums import TypeUpdate
from app.schemas.message import Message


CommandsServicesType = Union[
    CommandStartService,
    CommandAddFeedService,
    CommandListFeedService,
    CommandDeleteFeedService,
    CallbackService,
]


async def get_current_user(
    users_service: UsersService = Depends(get_users_service),
    update: Union[Message, Callback] = Body(...),
) -> User:
    user = await users_service.get_or_create(update)
    if not user.active:
        logger.info("Юзер найден, но не активен.")
        await users_service.activate_user(user.chat_id)
    return user


def get_command_service(
    update: Union[Message, Callback] = Body(...),
    start_service: CommandStartService = Depends(get_command_start_service),
    add_feed_service: CommandStartService = Depends(get_command_add_feed_service),
    list_feed_service: CommandStartService = Depends(get_command_list_feed_service),
    delete_feed_service: CommandStartService = Depends(get_command_delete_feed_service),
    authorize_service: AuthorizeService = Depends(get_command_authorize_service),
    authorize_pocket_service: AuthorizePocketService = Depends(get_authorize_pocket_service),
    unauthorize_pocket_service: UnAuthorizePocketService = Depends(get_unauthorize_pocket_service),
    callback_service: CallbackService = Depends(get_callback_service),
) -> Optional[CommandsServicesType]:
    if update.type_update is TypeUpdate.callback:
        return callback_service
    commands_map = {
        "start": start_service,
        "add_feed": add_feed_service,
        "list_feed": list_feed_service,
        "delete_feed": delete_feed_service,
        "authorize": authorize_service,
        "authorize_pocket": authorize_pocket_service,
        "unauthorize_pocket": unauthorize_pocket_service,
    }
    return commands_map.get(update.message.command)  # type: ignore  # FIXME
