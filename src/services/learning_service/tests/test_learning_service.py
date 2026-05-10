from services.common.models import AuditEvent, LearningTelemetry
from services.learning_service.core import LearningService
from services.workflow_support import InMemoryAuditRepository, InMemoryLearningRepository


def test_learning_ingest_uses_audit_context():
    service = LearningService(InMemoryLearningRepository(), InMemoryAuditRepository())
    record = service.ingest(
        LearningTelemetry(
            outcome_id="o1",
            tenant_id="t1",
            recommendation_id="r1",
            decision_id="d1",
            outcome="SUCCESS",
            metrics={"quality": 0.8},
        ),
        [AuditEvent(event_id="e1", tenant_id="t1", correlation_id="d1", event_type="decision.approved", resource_id="d1", payload={})],
    )
    assert record.signal > 0.0
    assert "decision.approved" in record.notes


def test_learning_dataset_filters_by_tenant():
    service = LearningService(InMemoryLearningRepository(), InMemoryAuditRepository())
    service.ingest(LearningTelemetry(outcome_id="o1", tenant_id="t1", recommendation_id="r1", decision_id="d1", outcome="PARTIAL"))
    service.ingest(LearningTelemetry(outcome_id="o2", tenant_id="t2", recommendation_id="r2", decision_id="d2", outcome="FAILURE"))
    assert len(service.dataset("t1")) == 1
