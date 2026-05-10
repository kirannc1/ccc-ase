from services.action_adapters.core import ActionAdaptersService
from services.common.models import ActionExecutionRequest


def test_adapter_registry():
    service = ActionAdaptersService()
    assert service.list_adapters() == ["db", "event", "rest"]


def test_rest_adapter_execute():
    service = ActionAdaptersService()
    result = service.execute(
        "rest",
        ActionExecutionRequest(action_id="a1", tenant_id="t1", recommendation_id="r1", adapter_name="rest", payload={"x": 1}),
    )
    assert result["adapter"] == "rest"

