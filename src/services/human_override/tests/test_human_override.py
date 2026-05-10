from services.common.models import OverrideRequest
from services.human_override.core import HumanOverrideService
from services.workflow_support import InMemoryAuditRepository, InMemoryOverrideRepository


def test_override_precedence():
    service = HumanOverrideService(InMemoryOverrideRepository(), InMemoryAuditRepository())
    record = service.apply(
        OverrideRequest(
            tenant_id="t1",
            recommendation_id="r1",
            decision_id="d1",
            actor_id="a1",
            reason="manual review",
            override_status="REJECTED",
        )
    )
    assert service.effective_status("d1", "APPROVED") == "REJECTED"
    assert record.actor_id == "a1"


def test_override_default_passthrough():
    service = HumanOverrideService(InMemoryOverrideRepository(), InMemoryAuditRepository())
    assert service.effective_status("missing", "APPROVED") == "APPROVED"

