from __future__ import annotations

import logging
from typing import Iterable

from services.common.models import (
    ActionExecutionRequest,
    ActionExecutionResult,
    ApprovalRecord,
    ApprovalRequest,
    ApprovalStage,
    ApprovalTransitionRequest,
    AuditEvent,
    LearningRecord,
    LearningTelemetry,
    ModelMetadata,
    ModelRegistrationRequest,
    OverrideRecord,
    OverrideRequest,
    ReplayArtifact,
    ReplayRequest,
)
from services.workflow_support import (
    ActionAdapter,
    ApprovalRepository,
    AuditRepository,
    ExecutionRepository,
    InMemoryApprovalRepository,
    InMemoryAuditRepository,
    InMemoryExecutionRepository,
    InMemoryLearningRepository,
    InMemoryModelRegistryRepository,
    InMemoryOverrideRepository,
    LearningRepository,
    ModelRegistryRepository,
    OverrideRepository,
    MockDatabaseAdapter,
    MockEventAdapter,
    MockRestAdapter,
    new_id,
    utc_now,
)


logger = logging.getLogger(__name__)


class ApprovalWorkflowService:
    def __init__(self, repository: ApprovalRepository | None = None, audit: AuditRepository | None = None) -> None:
        self.repository = repository or InMemoryApprovalRepository()
        self.audit = audit or InMemoryAuditRepository()

    def start(self, request: ApprovalRequest) -> ApprovalRecord:
        stages = request.stages or [ApprovalStage(stage_id=new_id("stage"), name="manager_review", required_roles=["manager"])]
        record = ApprovalRecord(
            approval_id=new_id("approval"),
            tenant_id=request.tenant_id,
            recommendation_id=request.recommendation_id,
            requested_by=request.requested_by,
            status="PENDING",
            stages=stages,
            metadata=request.metadata,
            history=[{"action": "created", "stage": stages[0].name, "at": utc_now().isoformat()}],
        )
        self.repository.save(record)
        self.audit.append(self._event(record.tenant_id, record.approval_id, "approval.created", record.model_dump()))
        return record

    def transition(self, request: ApprovalTransitionRequest) -> ApprovalRecord:
        record = self.repository.get(request.approval_id)
        if record is None:
            raise KeyError(request.approval_id)
        if record.status != "PENDING":
            return record
        stage = record.stages[min(record.current_stage_index, len(record.stages) - 1)]
        if request.action == "approve":
            if stage.required_roles and request.actor_role not in stage.required_roles:
                raise PermissionError("role not allowed")
            record.history.append({"action": "approve", "stage": stage.name, "actor": request.actor_id, "at": utc_now().isoformat()})
            if record.current_stage_index + 1 >= len(record.stages):
                record.status = "APPROVED"
                record.decided_by = request.actor_id
                record.decided_reason = request.reason
            else:
                record.current_stage_index += 1
        else:
            record.status = "REJECTED"
            record.decided_by = request.actor_id
            record.decided_reason = request.reason
            record.history.append({"action": "reject", "stage": stage.name, "actor": request.actor_id, "at": utc_now().isoformat()})
        record.updated_at = utc_now()
        self.repository.save(record)
        self.audit.append(self._event(record.tenant_id, record.approval_id, "approval.transitioned", record.model_dump()))
        return record

    def _event(self, tenant_id: str, resource_id: str, event_type: str, payload: dict) -> AuditEvent:
        return AuditEvent(event_id=new_id("evt"), tenant_id=tenant_id, correlation_id=resource_id, event_type=event_type, resource_id=resource_id, payload=payload)


class HumanOverrideService:
    def __init__(self, repository: OverrideRepository | None = None, audit: AuditRepository | None = None) -> None:
        self.repository = repository or InMemoryOverrideRepository()
        self.audit = audit or InMemoryAuditRepository()

    def apply(self, request: OverrideRequest) -> OverrideRecord:
        record = OverrideRecord(
            override_id=new_id("override"),
            tenant_id=request.tenant_id,
            recommendation_id=request.recommendation_id,
            decision_id=request.decision_id,
            actor_id=request.actor_id,
            reason=request.reason,
            override_status=request.override_status,
        )
        self.repository.save(record)
        self.audit.append(AuditEvent(event_id=new_id("evt"), tenant_id=request.tenant_id, correlation_id=request.decision_id, event_type="decision.overridden", resource_id=request.decision_id, payload=record.model_dump()))
        return record

    def effective_status(self, decision_id: str, system_status: str) -> str:
        override = self.repository.get_by_decision(decision_id)
        return override.override_status if override else system_status


class ExecutionOrchestratorService:
    def __init__(
        self,
        repository: ExecutionRepository | None = None,
        audit: AuditRepository | None = None,
        adapters: Iterable[ActionAdapter] | None = None,
    ) -> None:
        self.repository = repository or InMemoryExecutionRepository()
        self.audit = audit or InMemoryAuditRepository()
        self.adapters = {adapter.name: adapter for adapter in (adapters or [MockRestAdapter(), MockDatabaseAdapter(), MockEventAdapter()])}

    def dispatch(self, request: ActionExecutionRequest) -> ActionExecutionResult:
        existing = self.repository.get(request.action_id)
        if existing:
            return existing
        if request.async_mode:
            result = ActionExecutionResult(action_id=request.action_id, tenant_id=request.tenant_id, recommendation_id=request.recommendation_id, adapter_name=request.adapter_name, status="QUEUED", attempts=0, details={"mode": "async"})
            self.repository.save(result)
            self.audit.append(self._event(request.tenant_id, request.action_id, "execution.queued", result.model_dump()))
            return result
        adapter = self.adapters.get(request.adapter_name)
        if adapter is None:
            raise KeyError(request.adapter_name)
        errors: list[str] = []
        attempts = 0
        for attempt in range(1, request.max_retries + 2):
            attempts = attempt
            try:
                details = adapter.execute(request)
                result = ActionExecutionResult(action_id=request.action_id, tenant_id=request.tenant_id, recommendation_id=request.recommendation_id, adapter_name=request.adapter_name, status="SUCCEEDED", attempts=attempts, details=details)
                self.repository.save(result)
                self.audit.append(self._event(request.tenant_id, request.action_id, "execution.succeeded", result.model_dump()))
                return result
            except Exception as exc:  # pragma: no cover - defensive
                logger.debug("adapter failure: %s", exc)
                errors.append(str(exc))
        result = ActionExecutionResult(action_id=request.action_id, tenant_id=request.tenant_id, recommendation_id=request.recommendation_id, adapter_name=request.adapter_name, status="FAILED", attempts=attempts, details={"errors": errors})
        self.repository.save(result)
        self.audit.append(self._event(request.tenant_id, request.action_id, "execution.failed", result.model_dump()))
        return result

    def _event(self, tenant_id: str, resource_id: str, event_type: str, payload: dict) -> AuditEvent:
        return AuditEvent(event_id=new_id("evt"), tenant_id=tenant_id, correlation_id=resource_id, event_type=event_type, resource_id=resource_id, payload=payload)


class AuditTrailService:
    def __init__(self, repository: AuditRepository | None = None) -> None:
        self.repository = repository or InMemoryAuditRepository()

    def record(self, event: AuditEvent) -> AuditEvent:
        return self.repository.append(event)

    def replay(self, request: ReplayRequest) -> ReplayArtifact:
        events = self.repository.find(request.tenant_id, request.correlation_id, request.resource_id)
        deduped: dict[str, AuditEvent] = {}
        for event in events:
            deduped.setdefault(event.event_id, event)
        return ReplayArtifact(tenant_id=request.tenant_id, events=list(deduped.values()))


class ModelRegistryService:
    def __init__(self, repository: ModelRegistryRepository | None = None, audit: AuditRepository | None = None) -> None:
        self.repository = repository or InMemoryModelRegistryRepository()
        self.audit = audit or InMemoryAuditRepository()

    def register(self, request: ModelRegistrationRequest) -> ModelMetadata:
        metadata = ModelMetadata(model_id=request.model_id, name=request.name, version=request.version, config=request.config, status=request.status)
        self.repository.save(metadata)
        self.audit.append(AuditEvent(event_id=new_id("evt"), tenant_id="system", correlation_id=request.model_id, event_type="model.registered", resource_id=request.model_id, payload=metadata.model_dump()))
        return metadata

    def activate(self, model_id: str, version: str) -> ModelMetadata:
        metadata = self.repository.get(model_id, version)
        if metadata is None:
            raise KeyError(model_id)
        metadata.status = "ACTIVE"
        metadata.updated_at = utc_now()
        self.repository.save(metadata)
        return metadata

    def deactivate(self, model_id: str, version: str) -> ModelMetadata:
        metadata = self.repository.get(model_id, version)
        if metadata is None:
            raise KeyError(model_id)
        metadata.status = "INACTIVE"
        metadata.updated_at = utc_now()
        self.repository.save(metadata)
        return metadata

    def lookup(self, model_id: str, version: str | None = None) -> ModelMetadata | None:
        return self.repository.get(model_id, version)


class LearningService:
    def __init__(self, repository: LearningRepository | None = None, audit: AuditRepository | None = None) -> None:
        self.repository = repository or InMemoryLearningRepository()
        self.audit = audit or InMemoryAuditRepository()

    def ingest(self, telemetry: LearningTelemetry, audit_events: list[AuditEvent] | None = None) -> LearningRecord:
        signal_base = {"SUCCESS": 1.0, "PARTIAL": 0.5, "FAILURE": 0.0}[telemetry.outcome]
        metric_score = sum(telemetry.metrics.values()) / max(1, len(telemetry.metrics))
        audit_bonus = 0.05 * len(audit_events or [])
        record = LearningRecord(
            learning_id=new_id("learn"),
            tenant_id=telemetry.tenant_id,
            recommendation_id=telemetry.recommendation_id,
            decision_id=telemetry.decision_id,
            signal=round(min(1.0, signal_base + (metric_score * 0.1) + audit_bonus), 3),
            notes=[event.event_type for event in (audit_events or [])[:3]],
        )
        self.repository.save(record)
        self.audit.append(AuditEvent(event_id=new_id("evt"), tenant_id=telemetry.tenant_id, correlation_id=telemetry.decision_id, event_type="learning.ingested", resource_id=telemetry.decision_id, payload=record.model_dump()))
        return record

    def dataset(self, tenant_id: str | None = None) -> list[LearningRecord]:
        return self.repository.list(tenant_id)
