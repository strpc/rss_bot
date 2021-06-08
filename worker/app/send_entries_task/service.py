import json
from typing import Any, Dict, List, Optional

from app.clients.database import Database
from app.clients.telegram import Telegram
from app.feeds.models import UserEntry
from app.feeds.service import FeedsService
from app.send_entries_task.models import Button, PocketButton
from app.users.models import PocketIntegraion
from app.users.service import UsersService
from app.utils import bold_markdown, shielding_markdown_text


class SenderMessages:
    def __init__(
        self,
        *,
        db: Database,
        feeds_service: FeedsService,
        users_service: UsersService,
        telegram: Telegram,
    ):
        self._db = db
        self._feeds_service = feeds_service
        self._users_service = users_service
        self._telegram = telegram

    @staticmethod
    def _format_text(entry: UserEntry) -> str:
        title = bold_markdown(shielding_markdown_text(entry.title)) if entry.title else ""
        text = shielding_markdown_text(entry.text) if entry.text else ""
        return f"{title}\n\n{text}\n\n{shielding_markdown_text(entry.url)}"  # type: ignore

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
        entry: UserEntry,
        user_integration: Optional[PocketIntegraion],
    ) -> Dict[str, Any]:
        text = self._format_text(entry)
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

    async def send(self) -> None:
        new_entries = await self._feeds_service.get_unsended_entries()
        if new_entries is None:
            return

        for entry in new_entries:
            user_integration = await self._users_service.get_user_integration(entry.chat_id)
            message_body = await self._create_message(entry, user_integration)
            await self._telegram.send_raw_message(message_body)
