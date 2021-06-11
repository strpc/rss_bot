from app.core.commands.command_abc import CommandServiceABC
from app.schemas.callback import Callback, CallbackIntegrationServicePayload
from app.schemas.enums import ServiceIntegration


class CallbackService(CommandServiceABC):
    @staticmethod
    def _get_service_integration(name: ServiceIntegration):  # type: ignore
        services = {
            ServiceIntegration.pocket: "pocket",
        }
        return services[name]

    async def handle(self, update: Callback) -> None:
        payload = CallbackIntegrationServicePayload.parse_raw(update.callback_query.data)
        service = self._get_service_integration(payload.service)
        print(service)
        print(update.callback_query.id)
        print(update)
