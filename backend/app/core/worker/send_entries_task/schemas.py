from app.api.schemas.callback import CallbackIntegrationServicePayload
from app.api.schemas.enums import ServiceIntegration
from app.api.schemas.message import Button


class PocketButton(Button):
    service = ServiceIntegration.pocket
    text = "Save to Pocket \U0001F516"

    def add_callback_data(self, entry_id: int) -> None:
        self.callback_data = CallbackIntegrationServicePayload(
            service=self.service,
            entry_id=entry_id,
            sended=False,
        ).json()
