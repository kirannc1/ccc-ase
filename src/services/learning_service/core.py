from services.common.models import AuditEvent, LearningRecord, LearningTelemetry
from services.workflow_support import AuditRepository, InMemoryAuditRepository, InMemoryLearningRepository, LearningRepository, new_id


class LearningService:
    def __init__(self, repository: LearningRepository | None = None, audit: AuditRepository | None = None) -> None:
        self.repository = repository or InMemoryLearningRepository()
        self.audit = audit or InMemoryAuditRepository()

    def ingest(self, telemetry: LearningTelemetry, audit_events: list[AuditEvent] | None = None) -> LearningRecord:
        signal_base = {"SUCCESS": 1.0, "PARTIAL": 0.5, "FAILURE": 0.0}[telemetry.outcome]
        metric_score = sum(telemetry.metrics.values()) / max(1, len(telemetry.metrics))
        record = LearningRecord(
            learning_id=new_id("learn"),
            tenant_id=telemetry.tenant_id,
            recommendation_id=telemetry.recommendation_id,
            decision_id=telemetry.decision_id,
            signal=round(min(1.0, signal_base + (metric_score * 0.1) + (0.05 * len(audit_events or []))), 3),
            notes=[event.event_type for event in (audit_events or [])[:3]],
        )
        self.repository.save(record)
        self.audit.append(AuditEvent(event_id=new_id("evt"), tenant_id=telemetry.tenant_id, correlation_id=telemetry.decision_id, event_type="learning.ingested", resource_id=telemetry.decision_id, payload=record.model_dump()))
        return record

    def dataset(self, tenant_id: str | None = None) -> list[LearningRecord]:
        return self.repository.list(tenant_id)

