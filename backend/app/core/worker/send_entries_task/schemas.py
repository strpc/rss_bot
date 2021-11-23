from app.api.endpoints.update.enums import ServiceIntegration
from app.api.endpoints.update.schemas import Button, CallbackIntegrationServicePayload


class PocketButton(Button):
    service = ServiceIntegration.pocket
    text = u"Save to Pocket \U0001F516"

    def add_callback_data(self, entry_id: int) -> None:
        self.callback_data = CallbackIntegrationServicePayload(
            service=self.service,
            entry_id=entry_id,
            sended=False,
        ).json()
