from app.schemas.callback import CallbackIntegrationServicePayload
from app.schemas.enums import ServiceIntegration
from app.schemas.message import Button


class PocketButton(Button):
    service = ServiceIntegration.pocket
    text = "Save to Pocket"

    def add_callback_data(self, entry_id: int) -> None:
        self.callback_data = CallbackIntegrationServicePayload(
            service=self.service,
            entry_id=entry_id,
            sended=False,
        ).json()
