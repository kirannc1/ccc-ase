from services.common.models import ActionExecutionRequest
from services.execution_orchestrator.core import ExecutionOrchestratorService
from services.workflow_support import InMemoryAuditRepository, InMemoryExecutionRepository, MockRestAdapter


class FailingAdapter:
    name = "failing"

    def execute(self, request):
        raise RuntimeError("boom")


def test_execution_success_and_idempotency():
    service = ExecutionOrchestratorService(InMemoryExecutionRepository(), InMemoryAuditRepository(), [MockRestAdapter()])
    first = service.dispatch(
        ActionExecutionRequest(
            action_id="a1",
            tenant_id="t1",
            recommendation_id="r1",
            adapter_name="rest",
            payload={"x": 1},
        )
    )
    second = service.dispatch(
        ActionExecutionRequest(
            action_id="a1",
            tenant_id="t1",
            recommendation_id="r1",
            adapter_name="rest",
            payload={"x": 2},
        )
    )
    assert first.status == "SUCCEEDED"
    assert second.details["echo"] == {"x": 1}


def test_execution_retry_failure():
    service = ExecutionOrchestratorService(InMemoryExecutionRepository(), InMemoryAuditRepository(), [FailingAdapter()])
    result = service.dispatch(
        ActionExecutionRequest(
            action_id="a2",
            tenant_id="t1",
            recommendation_id="r1",
            adapter_name="failing",
            attempts=1,
            max_retries=1,
        )
    )
    assert result.status == "FAILED"
    assert result.attempts == 2
