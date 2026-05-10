from services.approval_workflow.core import ApprovalWorkflowService
from services.common.models import ApprovalRequest, ApprovalStage, ApprovalTransitionRequest
from services.workflow_support import InMemoryApprovalRepository, InMemoryAuditRepository


def test_approval_workflow_happy_path():
    service = ApprovalWorkflowService(InMemoryApprovalRepository(), InMemoryAuditRepository())
    record = service.start(
        ApprovalRequest(
            tenant_id="t1",
            recommendation_id="r1",
            requested_by="u1",
            stages=[ApprovalStage(stage_id="s1", name="manager", required_roles=["manager"])],
        )
    )
    approved = service.transition(
        ApprovalTransitionRequest(approval_id=record.approval_id, actor_id="m1", actor_role="manager", action="approve")
    )
    assert approved.status == "APPROVED"
    assert approved.decided_by == "m1"


def test_approval_workflow_rejects_wrong_role():
    service = ApprovalWorkflowService(InMemoryApprovalRepository(), InMemoryAuditRepository())
    record = service.start(ApprovalRequest(tenant_id="t1", recommendation_id="r1", requested_by="u1"))
    try:
        service.transition(
            ApprovalTransitionRequest(approval_id=record.approval_id, actor_id="e1", actor_role="employee", action="approve")
        )
        raise AssertionError("expected PermissionError")
    except PermissionError:
        assert True

