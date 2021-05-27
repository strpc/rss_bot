from typing import Optional, Union

from fastapi import Body, Depends
from loguru import logger

from app.core.commands.add_feed.deps import get_command_add_feed_service
from app.core.commands.add_feed.service import CommandAddFeedService
from app.core.commands.delete_feed.deps import get_command_delete_feed_service
from app.core.commands.delete_feed.service import CommandDeleteFeedService
from app.core.commands.list_feed.deps import get_command_list_feed_service
from app.core.commands.list_feed.service import CommandListFeedService
from app.core.commands.start.deps import get_command_start_service
from app.core.commands.start.service import CommandStartService
from app.core.users.deps import get_users_service
from app.core.users.models import User
from app.core.users.service import UsersService
from app.schemas.message import Message


CommandsServicesType = Union[
    CommandStartService, CommandAddFeedService, CommandListFeedService, CommandDeleteFeedService
]


async def get_current_user(
    users_service: UsersService = Depends(get_users_service),
    update: Message = Body(...),
) -> User:
    user = await users_service.get_or_create(update)
    if not user.active:
        logger.info("Юзер найден, но не активен.")
        await users_service.activate_user(user.chat_id)
    return user


def get_command_service(
    update: Message = Body(...),
    command_start_service: CommandStartService = Depends(get_command_start_service),
    command_add_feed_service: CommandStartService = Depends(get_command_add_feed_service),
    command_list_feed_service: CommandStartService = Depends(get_command_list_feed_service),
    command_delete_feed_service: CommandStartService = Depends(get_command_delete_feed_service),
) -> Optional[CommandsServicesType]:
    commands_map = {
        "start": command_start_service,
        "add_feed": command_add_feed_service,
        "list_feed": command_list_feed_service,
        "delete_feed": command_delete_feed_service,
    }
    return commands_map.get(update.message.command)  # type: ignore  # FIXME
