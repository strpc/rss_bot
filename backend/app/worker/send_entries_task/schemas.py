from typing import Any, Dict, Union

from pydantic import BaseModel, validator

from app.api.endpoints.update.enums import ServiceIntegration
from app.api.endpoints.update.schemas import CallbackIntegrationServicePayload


SAVE_POCKET_EMOJI = "\U0001F516"


class PocketButton(BaseModel):
    service: ServiceIntegration = ServiceIntegration.pocket
    text: str = u"Save to Pocket {EMOJI}".format(EMOJI=SAVE_POCKET_EMOJI)
    callback_data: Union[str, int]

    @validator("callback_data", pre=True, always=True)
    def validate_callback_data(cls, field_value: int, values: Dict[str, Any], **kwargs: Any) -> str:
        callback_data = CallbackIntegrationServicePayload(
            service=values["service"],
            entry_id=field_value,
            sended=False,
        ).json()
        return callback_data
