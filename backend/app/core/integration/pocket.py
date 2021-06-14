from typing import Optional

from loguru import logger

from app.core.clients.pocket import PocketClient, PocketError
from app.core.integration.integration_abc import ExternalServiceABC
from app.core.users.service import UsersService


class PocketIntegration(ExternalServiceABC):
    success_message = "Saved"

    def __init__(self, pocket_client: PocketClient, users_service: UsersService):
        self._pocket_client = pocket_client
        self._users_service = users_service

    async def _disable_integration(
        self,
        chat_id: int,
        error_code: Optional[int] = None,
        error_message: Optional[str] = None,
        status_code: Optional[int] = None,
    ) -> None:
        self.success_message = "ERROR"
        user = await self._users_service.get_user(chat_id)
        await self._users_service.disable_pocket_integration(
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
        return await self._users_service.get_access_token(chat_id)

    async def send(self, *, chat_id: int, url: str) -> None:
        logger.debug("Сохраняем {}...", url)

        access_token = await self._get_access_token(chat_id)
        if access_token is None:
            logger.warning("Не нашли access_token. chat_id={}", chat_id)
            await self._disable_integration(chat_id)
            return

        await self._add_item(
            chat_id=chat_id,
            access_token=access_token,
            url=url,
        )

    def get_update_message(self) -> str:  # type: ignore
        return self.success_message
