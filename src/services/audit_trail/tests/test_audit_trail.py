from services.audit_trail.core import AuditTrailService
from services.common.models import AuditEvent, ReplayRequest
from services.workflow_support import InMemoryAuditRepository


def test_audit_replay_deduplicates():
    repo = InMemoryAuditRepository()
    service = AuditTrailService(repo)
    event = AuditEvent(event_id="e1", tenant_id="t1", correlation_id="c1", event_type="decision.created", resource_id="r1", payload={"x": 1})
    repo.append(event)
    repo.append(event)
    replay = service.replay(ReplayRequest(tenant_id="t1", correlation_id="c1"))
    assert len(replay.events) == 1


def test_audit_record_roundtrip():
    service = AuditTrailService(InMemoryAuditRepository())
    event = AuditEvent(event_id="e2", tenant_id="t1", correlation_id="c2", event_type="decision.updated", resource_id="r2", payload={})
    assert service.record(event).event_id == "e2"

