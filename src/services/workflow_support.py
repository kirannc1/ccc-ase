from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Protocol
from uuid import uuid4

from services.common.models import (
    ActionExecutionRequest,
    ActionExecutionResult,
    ApprovalRecord,
    AuditEvent,
    LearningRecord,
    ModelMetadata,
    OverrideRecord,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class ApprovalRepository(Protocol):
    def save(self, record: ApprovalRecord) -> ApprovalRecord: ...

    def get(self, approval_id: str) -> ApprovalRecord | None: ...


class OverrideRepository(Protocol):
    def save(self, record: OverrideRecord) -> OverrideRecord: ...

    def get_by_decision(self, decision_id: str) -> OverrideRecord | None: ...


class ExecutionRepository(Protocol):
    def save(self, result: ActionExecutionResult) -> ActionExecutionResult: ...

    def get(self, action_id: str) -> ActionExecutionResult | None: ...


class AuditRepository(Protocol):
    def append(self, event: AuditEvent) -> AuditEvent: ...

    def find(self, tenant_id: str, correlation_id: str | None = None, resource_id: str | None = None) -> list[AuditEvent]: ...

    def get(self, event_id: str) -> AuditEvent | None: ...


class ModelRegistryRepository(Protocol):
    def save(self, metadata: ModelMetadata) -> ModelMetadata: ...

    def get(self, model_id: str, version: str | None = None) -> ModelMetadata | None: ...

    def list(self, model_id: str | None = None) -> list[ModelMetadata]: ...


class LearningRepository(Protocol):
    def save(self, record: LearningRecord) -> LearningRecord: ...

    def list(self, tenant_id: str | None = None) -> list[LearningRecord]: ...


class ActionAdapter(Protocol):
    name: str

    def execute(self, request: ActionExecutionRequest) -> dict[str, Any]: ...


class InMemoryApprovalRepository:
    def __init__(self) -> None:
        self._records: dict[str, ApprovalRecord] = {}

    def save(self, record: ApprovalRecord) -> ApprovalRecord:
        self._records[record.approval_id] = record
        return record

    def get(self, approval_id: str) -> ApprovalRecord | None:
        return self._records.get(approval_id)


class InMemoryOverrideRepository:
    def __init__(self) -> None:
        self._records: dict[str, OverrideRecord] = {}

    def save(self, record: OverrideRecord) -> OverrideRecord:
        self._records[record.decision_id] = record
        return record

    def get_by_decision(self, decision_id: str) -> OverrideRecord | None:
        return self._records.get(decision_id)


class InMemoryExecutionRepository:
    def __init__(self) -> None:
        self._records: dict[str, ActionExecutionResult] = {}

    def save(self, result: ActionExecutionResult) -> ActionExecutionResult:
        self._records[result.action_id] = result
        return result

    def get(self, action_id: str) -> ActionExecutionResult | None:
        return self._records.get(action_id)


class InMemoryAuditRepository:
    def __init__(self) -> None:
        self._records: dict[str, AuditEvent] = {}

    def append(self, event: AuditEvent) -> AuditEvent:
        self._records.setdefault(event.event_id, event)
        return self._records[event.event_id]

    def find(self, tenant_id: str, correlation_id: str | None = None, resource_id: str | None = None) -> list[AuditEvent]:
        rows = [event for event in self._records.values() if event.tenant_id == tenant_id]
        if correlation_id is not None:
            rows = [event for event in rows if event.correlation_id == correlation_id]
        if resource_id is not None:
            rows = [event for event in rows if event.resource_id == resource_id]
        return sorted(rows, key=lambda event: event.created_at)

    def get(self, event_id: str) -> AuditEvent | None:
        return self._records.get(event_id)


class InMemoryModelRegistryRepository:
    def __init__(self) -> None:
        self._records: dict[tuple[str, str], ModelMetadata] = {}

    def save(self, metadata: ModelMetadata) -> ModelMetadata:
        self._records[(metadata.model_id, metadata.version)] = metadata
        return metadata

    def get(self, model_id: str, version: str | None = None) -> ModelMetadata | None:
        if version is not None:
            return self._records.get((model_id, version))
        versions = [record for (record_model_id, _), record in self._records.items() if record_model_id == model_id]
        return versions[-1] if versions else None

    def list(self, model_id: str | None = None) -> list[ModelMetadata]:
        rows = list(self._records.values())
        if model_id is not None:
            rows = [record for record in rows if record.model_id == model_id]
        return sorted(rows, key=lambda record: (record.model_id, record.version))


class InMemoryLearningRepository:
    def __init__(self) -> None:
        self._records: dict[str, LearningRecord] = {}

    def save(self, record: LearningRecord) -> LearningRecord:
        self._records[record.learning_id] = record
        return record

    def list(self, tenant_id: str | None = None) -> list[LearningRecord]:
        rows = list(self._records.values())
        if tenant_id is not None:
            rows = [record for record in rows if record.tenant_id == tenant_id]
        return sorted(rows, key=lambda record: record.created_at)


class MockRestAdapter:
    name = "rest"

    def execute(self, request: ActionExecutionRequest) -> dict[str, Any]:
        return {"adapter": self.name, "echo": request.payload, "status": "sent"}


class MockDatabaseAdapter:
    name = "db"

    def execute(self, request: ActionExecutionRequest) -> dict[str, Any]:
        return {"adapter": self.name, "row_count": len(request.payload), "status": "written"}


class MockEventAdapter:
    name = "event"

    def execute(self, request: ActionExecutionRequest) -> dict[str, Any]:
        return {"adapter": self.name, "topic": request.adapter_name, "status": "published"}
