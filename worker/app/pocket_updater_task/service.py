from loguru import logger

from app.pocket.service import PocketService
from app.users.service import UsersService


class PocketUpdater:
    def __init__(
        self,
        pocket_service: PocketService,
        users_service: UsersService,
    ):
        self._pocket_service = pocket_service
        self._users_service = users_service

    async def update(self) -> None:
        request_tokens = await self._users_service.get_new_request_token()
        if request_tokens is None:
            return

        logger.debug("Пытаемся получить access токены...")
        for request_token in request_tokens:
            logger.debug("Обрабатываем {}...", request_token)

            access_token = await self._pocket_service.get_access_token(request_token)
            if access_token is not None:
                logger.debug("Получили access_token. Обновим его в базе...")
                await self._users_service.update_access_token(
                    request_token=request_token,
                    access_token=access_token,
                )
