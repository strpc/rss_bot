class ExternalServices:
    def __init__(self, pocket_service):  # type: ignore
        self._pocket_service = pocket_service

    @property
    def pocket(self):  # type: ignore
        return self._pocket_service
