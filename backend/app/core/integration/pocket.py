from typing import Any, Dict, List, Optional

from loguru import logger

from app.clients.pocket import PocketClient, PocketError
from app.core.integration.exceptions import SendingError
from app.core.integration.integration_abc import ExternalServiceABC
from app.core.integration.repository import PocketRepository
from app.core.users.service import UsersService


class PocketIntegration(ExternalServiceABC):
    success_message = "Saved \U00002705"
    error_message = "ERROR \U0000274C"

    def __init__(
        self,
        *,
        pocket_client: PocketClient,
        users_service: UsersService,
        repository: PocketRepository,
    ):
        self._pocket_client = pocket_client
        self._users_service = users_service
        self._repository = repository

    async def _disable_integration(
        self,
        chat_id: int,
        error_code: Optional[int] = None,
        error_message: Optional[str] = None,
        status_code: Optional[int] = None,
    ) -> None:
        user = await self._users_service.get_user(chat_id)
        await self.disable_pocket_integration(
            user_id=user.id,  # type: ignore
            error_code=error_code,
            error_message=error_message,
            status_code=status_code,
        )

    async def _add_item(self, chat_id: int, access_token: str, url: str) -> None:
        try:
            await self._pocket_client.add_item(access_token=access_token, url=url)
        except PocketError as error:
            logger.error("Ошибка при отправке новой записи.")
            await self._disable_integration(
                chat_id=chat_id,
                error_code=error.pocket_error_code,
                error_message=error.pocket_error_message,
                status_code=error.http_status_code,
            )

    async def _get_access_token(self, chat_id: int) -> Optional[str]:
        return await self._repository.get_access_token(chat_id)

    async def send(self, *, chat_id: int, url: str) -> None:
        logger.debug("Сохраняем {}...", url)

        access_token = await self._get_access_token(chat_id)
        if access_token is None:
            logger.warning("Не нашли access_token. chat_id={}", chat_id)
            await self._disable_integration(chat_id)
            raise SendingError
        try:
            await self._add_item(
                chat_id=chat_id,
                access_token=access_token,
                url=url,
            )
        except Exception as error:
            raise SendingError from error

    def get_update_message(self) -> str:  # type: ignore
        return self.success_message

    def get_error_message(self) -> str:
        return self.error_message

    async def get_new_request_token(self) -> Optional[List[Dict]]:
        return await self._repository.get_new_request_token()

    async def disable_pocket_integration(
        self,
        *,
        user_id: int,
        error_code: Optional[int] = None,
        error_message: Optional[str] = None,
        status_code: Optional[int] = None,
    ) -> None:
        logger.info("Отключаем интеграцию у юзера user_id={}...", user_id)
        await self._repository.disable_pocket_integration(
            user_id=user_id,
            error_code=error_code,
            error_message=error_message,
            status_code=status_code,
        )

    async def update_access_token(
        self,
        user_id: int,
        access_token: Dict[str, Any],
    ) -> None:
        token = access_token.get("access_token")
        username = access_token.get("username")
        await self._repository.update_pocket_meta(
            user_id=user_id,
            access_token=token,  # type: ignore
            username=username,  # type: ignore
        )
