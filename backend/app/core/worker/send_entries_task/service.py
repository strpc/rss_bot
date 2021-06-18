from typing import Dict, List, Optional

from loguru import logger

from app.core.clients.database import Database
from app.core.clients.telegram import Telegram, TelegramBadBodyRequest, TelegramUserBlocked
from app.core.feeds.models import UserEntry
from app.core.feeds.service import FeedsService
from app.core.users.models import UserIntegration
from app.core.users.service import UsersService
from app.core.utils import bold_markdown, escape_md
from app.core.worker.send_entries_task.schemas import PocketButton
from app.schemas.enums import ParseMode
from app.schemas.message import Button


class SenderMessages:
    def __init__(
        self,
        *,
        database: Database,
        feeds_service: FeedsService,
        users_service: UsersService,
        telegram: Telegram,
    ):
        self._db = database
        self._feeds_service = feeds_service
        self._users_service = users_service
        self._telegram = telegram

    @staticmethod
    def _format_text(entry: UserEntry, limit_title: int, limit_text: int) -> str:
        title = entry.title or ""
        text = entry.text or ""
        url = escape_md(entry.url) or ""  # type: ignore
        cropped_title = title if len(title) < limit_title else f"{title[:limit_title]}..."
        cropped_text = text if len(text) < limit_text else f"{text[:limit_text]}..."
        bold_title = bold_markdown(escape_md(cropped_title))  # type: ignore
        shielded_text = escape_md(cropped_text)  # type: ignore
        return f"{bold_title}\n\n{shielded_text}\n\n{url}"

    @staticmethod
    def _create_buttons(
        entry: UserEntry,
        user_integration: UserIntegration,
    ) -> List[Button]:
        integration_services = []
        if user_integration.pocket_access_token is not None:
            pocket_button = PocketButton()
            pocket_button.add_callback_data(entry.id)
            integration_services.append(pocket_button)

        logger.debug("У пользователя {} активированных сервисов.", len(integration_services))
        return integration_services

    async def send(self, limit_title: int, limit_text: int) -> None:
        logger.info("Ищем новые записи для отправки пользователям...")
        new_entries = await self._feeds_service.get_unsended_entries()
        if new_entries is None:
            logger.info("Нет новых записей для отправки. exit...")
            return
        users_integrations: Dict[int, Optional[UserIntegration]] = {}
        logger.info("{} новых записей...", len(new_entries))
        for entry in new_entries:
            if entry.chat_id in users_integrations:
                user_integration = users_integrations[entry.chat_id]
            else:
                user_integration = await self._users_service.get_user_integration(entry.chat_id)
                users_integrations[entry.chat_id] = user_integration

            text = self._format_text(entry, limit_title, limit_text)
            buttons = None
            if user_integration is not None:
                buttons = self._create_buttons(
                    entry=entry,
                    user_integration=user_integration,
                )
            try:
                await self._telegram.send_message(
                    chat_id=entry.chat_id,
                    text=text,
                    inline_keyboard=buttons,
                    parse_mode=ParseMode.MarkdownV2,
                )
            except TelegramUserBlocked:
                logger.warning("Пользователь {} отключил бота.")
                await self._users_service.disable_user(entry.chat_id)

            except TelegramBadBodyRequest:
                logger.error("Ошибка при отправке записи id={}", entry.id)

            else:
                await self._feeds_service.mark_sended_entry(entry.id)
