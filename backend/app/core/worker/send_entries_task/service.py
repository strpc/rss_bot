from typing import List

from loguru import logger

from app.core.clients.database import Database
from app.core.clients.telegram import Telegram
from app.core.feeds.models import UserEntry
from app.core.feeds.service import FeedsService
from app.core.users.models import UserIntegration
from app.core.users.service import UsersService
from app.core.utils import bold_markdown, safetyed_markdown_text
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
        url = safetyed_markdown_text(entry.url) or ""  # type: ignore
        cropped_title = title if len(title) < limit_title else f"{title[:limit_title]}..."
        cropped_text = text if len(text) < limit_text else f"{text[:limit_text]}..."
        bold_title = bold_markdown(safetyed_markdown_text(cropped_title))  # type: ignore
        shielded_text = safetyed_markdown_text(cropped_text)  # type: ignore
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

        logger.info("У пользователя {} активированных сервисов.", len(integration_services))
        return integration_services

    async def send(self, limit_title: int, limit_text: int) -> None:
        new_entries = await self._feeds_service.get_unsended_entries()
        if new_entries is None:
            logger.info("Нет новых записей для отправки. exit...")
            return

        logger.info("Отправляем {} записей...", len(new_entries))
        sended_entries_id = []
        for entry in new_entries:
            user_integration = await self._users_service.get_user_integration(entry.chat_id)

            text = self._format_text(entry, limit_title, limit_text)
            buttons = None
            if user_integration is not None:

                buttons = self._create_buttons(
                    entry=entry,
                    user_integration=user_integration,
                )
            # todo: сделать проверку, что если не отправляется в маркдауне, то отправить без него
            # todo: сделать отключение пользователя если он вдруг отморозился
            await self._telegram.send_message(
                chat_id=entry.chat_id,
                text=text,
                inline_keyboard=buttons,
                parse_mode=ParseMode.MarkdownV2,
            )
            sended_entries_id.append(entry.id)
        await self._feeds_service.mark_sended_entries(sended_entries_id)
