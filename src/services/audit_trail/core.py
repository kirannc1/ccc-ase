from services.common.models import AuditEvent, ReplayArtifact, ReplayRequest
from services.workflow_support import AuditRepository, InMemoryAuditRepository, new_id


class AuditTrailService:
    def __init__(self, repository: AuditRepository | None = None) -> None:
        self.repository = repository or InMemoryAuditRepository()

    def record(self, event: AuditEvent) -> AuditEvent:
        return self.repository.append(event)

    def append(self, tenant_id: str, correlation_id: str, event_type: str, resource_id: str, payload: dict) -> AuditEvent:
        event = AuditEvent(event_id=new_id("evt"), tenant_id=tenant_id, correlation_id=correlation_id, event_type=event_type, resource_id=resource_id, payload=payload)
        return self.repository.append(event)

    def replay(self, request: ReplayRequest) -> ReplayArtifact:
        rows = self.repository.find(request.tenant_id, request.correlation_id, request.resource_id)
        seen: set[str] = set()
        events = []
        for event in rows:
            if event.event_id in seen:
                continue
            seen.add(event.event_id)
            events.append(event)
        return ReplayArtifact(tenant_id=request.tenant_id, events=events)

