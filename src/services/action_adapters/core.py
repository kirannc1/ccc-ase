from services.workflow_support import MockDatabaseAdapter, MockEventAdapter, MockRestAdapter


class ActionAdaptersService:
    def __init__(self) -> None:
        self.adapters = {adapter.name: adapter for adapter in [MockRestAdapter(), MockDatabaseAdapter(), MockEventAdapter()]}

    def list_adapters(self) -> list[str]:
        return sorted(self.adapters)

    def execute(self, adapter_name: str, request):
        adapter = self.adapters.get(adapter_name)
        if adapter is None:
            raise KeyError(adapter_name)
        return adapter.execute(request)

