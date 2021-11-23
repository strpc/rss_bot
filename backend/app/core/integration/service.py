from app.api.endpoints.update.enums import ServiceIntegration
from app.core.integration.integration_abc import ExternalServiceABC
from app.core.integration.pocket import PocketIntegration


class ExternalServices:
    def __init__(self, *, pocket_integration: PocketIntegration):
        self._pocket_integration = pocket_integration

    def get_service(self, name: ServiceIntegration) -> ExternalServiceABC:
        services = {
            ServiceIntegration.pocket: self.pocket,
        }
        return services[name]

    @property
    def pocket(self) -> ExternalServiceABC:
        return self._pocket_integration
