from fastapi import Depends

from app.core.base_deps import get_pocket_client
from app.core.clients.pocket import PocketClient
from app.core.integration.pocket import PocketIntegration
from app.core.integration.service import ExternalServices
from app.core.users.deps import get_users_service
from app.core.users.service import UsersService


def get_pocket_integration(
    pocket_client: PocketClient = Depends(get_pocket_client),
    users_service: UsersService = Depends(get_users_service),
) -> PocketIntegration:
    return PocketIntegration(
        pocket_client=pocket_client,
        users_service=users_service,
    )


def get_external_services(
    pocket_integration: PocketIntegration = Depends(get_pocket_integration),
) -> ExternalServices:
    return ExternalServices(
        pocket_integration=pocket_integration,
    )
