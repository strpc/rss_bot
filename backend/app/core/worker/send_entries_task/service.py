import json
from typing import Any, Dict, List, Optional

from loguru import logger

from app.core.clients.database import Database
from app.core.clients.telegram import Telegram
from app.core.feeds.models import UserEntry
from app.core.feeds.service import FeedsService
from app.core.users.models import PocketIntegraion
from app.core.users.service import UsersService
from app.core.utils import bold_markdown, safetyed_markdown_text
from app.core.worker.send_entries_task.models import Button, PocketButton


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
    def _format_body(
        chat_id: int,
        text: str,
        buttons: Optional[List[Button]] = None,
    ) -> Dict[str, Any]:
        body = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "MarkdownV2",
        }
        if buttons is not None:
            body["reply_markup"] = {"inline_keyboard": [[]]}
            for button in buttons:
                body["reply_markup"]["inline_keyboard"][0].append(  # type: ignore
                    {"text": button.title, "callback_data": button.callback_data},
                )
        return body

    async def _create_message(
        self,
        *,
        entry: UserEntry,
        user_integration: Optional[PocketIntegraion],
        limit_title: int,
        limit_text: int,
    ) -> Dict[str, Any]:
        text = self._format_text(entry, limit_title, limit_text)
        if user_integration is None:
            return self._format_body(entry.chat_id, text)

        integration_services = []
        if user_integration.pocket_access_token is not None:
            callback_data = {
                "service": "pocket",
                "entry_id": entry.id,
            }
            integration_services.append(PocketButton(callback_data=json.dumps(callback_data)))

        return self._format_body(entry.chat_id, text, integration_services)

    async def send(self, limit_title: int, limit_text: int) -> None:
        new_entries = await self._feeds_service.get_unsended_entries()
        if new_entries is None:
            logger.info("Нет новых записей для отправки. exit...")
            return

        sended_entries_id = []
        for entry in new_entries:
            user_integration = await self._users_service.get_user_integration(entry.chat_id)
            message_body = await self._create_message(
                entry=entry,
                user_integration=user_integration,
                limit_title=limit_title,
                limit_text=limit_text,
            )
            # todo: сделать проверку, что если не отправляется в маркдауне, то отправить без него
            # todo: сделать отключение пользователя если он вдруг отморозился
            await self._telegram.send_raw_message(message_body)
            sended_entries_id.append(entry.id)
        await self._feeds_service.mark_sended_entries(sended_entries_id)
