from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field


class Envelope(BaseModel):
    schema_version: str = "1.0"
    tenant_id: str
    correlation_id: str | None = None


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    service: str


class SourceRegistration(BaseModel):
    source_id: str
    source_name: str
    source_type: str
    config: dict[str, Any] = Field(default_factory=dict)


class RawRecord(BaseModel):
    schema_version: str = "1.0"
    tenant_id: str
    source_system: str
    source_record_id: str
    payload: dict[str, Any]
    observed_ts: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CanonicalEvent(BaseModel):
    schema_version: str = "1.0"
    event_id: str
    event_type: str
    tenant_id: str
    domain: str
    entity_refs: list[dict[str, str]] = Field(default_factory=list)
    payload: dict[str, Any]
    provenance: dict[str, str]


class EntityLink(BaseModel):
    schema_version: str = "1.0"
    tenant_id: str
    source_entity_id: str
    entity_id: str
    entity_type: str
    resolution_status: str = "resolved"


class FeatureRecord(BaseModel):
    schema_version: str = "1.0"
    tenant_id: str
    entity_id: str
    feature_name: str
    feature_version: str = "v1"
    value: float
    observed_ts: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class GraphRelation(BaseModel):
    schema_version: str = "1.0"
    tenant_id: str
    from_entity_id: str
    to_entity_id: str
    relation_type: str
    evidence_class: str = "statistically_supported_link"
    confidence: float = 0.5


class FeatureGenerationRequest(BaseModel):
    event: CanonicalEvent
    entity: EntityLink


class GraphWriteRequest(BaseModel):
    entity: EntityLink
    feature: FeatureRecord | None = None


class ParsedDocument(BaseModel):
    schema_version: str = "1.0"
    tenant_id: str
    document_id: str
    document_type: str
    extracted: dict[str, Any]


class SignalInsight(BaseModel):
    feature_name: str
    score: float
    rationale: str


class SignalIntelligenceRequest(BaseModel):
    tenant_id: str
    top_n: int = 5


class SignalIntelligenceResponse(BaseModel):
    tenant_id: str
    signals: list[SignalInsight] = Field(default_factory=list)


class ForecastRequest(BaseModel):
    tenant_id: str
    entity_id: str
    feature_name: str
    horizon: int = 1


class ForecastResponse(BaseModel):
    tenant_id: str
    entity_id: str
    feature_name: str
    forecast: float
    trend: float
    history: list[float] = Field(default_factory=list)


class AnomalyRequest(BaseModel):
    tenant_id: str
    feature_name: str
    value: float
    threshold: float = 3.0


class AnomalyResponse(BaseModel):
    tenant_id: str
    feature_name: str
    value: float
    mean: float
    stddev: float
    z_score: float
    anomaly: bool


class CausalRequest(BaseModel):
    tenant_id: str
    source_entity_id: str
    target_entity_id: str


class CausalResponse(BaseModel):
    tenant_id: str
    source_entity_id: str
    target_entity_id: str
    relation_type: str | None = None
    confidence: float
    explanation: str


class PolicyRequest(BaseModel):
    tenant_id: str
    metrics: dict[str, float] = Field(default_factory=dict)
    constraints: dict[str, float] = Field(default_factory=dict)


class PolicyResponse(BaseModel):
    tenant_id: str
    allowed: bool
    violations: list[str] = Field(default_factory=list)
    evaluated_metrics: dict[str, float] = Field(default_factory=dict)


class ScenarioSimulationRequest(BaseModel):
    tenant_id: str
    features: dict[str, float] = Field(default_factory=dict)
    graph_signals: list[str] = Field(default_factory=list)
    constraints: dict[str, float] = Field(default_factory=dict)


class ScenarioArtifact(BaseModel):
    scenario_id: str
    tenant_id: str
    name: str
    summary: str
    score: float
    assumptions: list[str] = Field(default_factory=list)
    impacts: dict[str, float] = Field(default_factory=dict)


class OptimizationRequest(BaseModel):
    tenant_id: str
    scenarios: list[ScenarioArtifact] = Field(default_factory=list)
    constraints: dict[str, float] = Field(default_factory=dict)


class RankedScenario(BaseModel):
    scenario_id: str
    score: float
    rationale: str


class OptimizationArtifact(BaseModel):
    tenant_id: str
    ranked_scenarios: list[RankedScenario] = Field(default_factory=list)
    best_scenario_id: str | None = None
    notes: list[str] = Field(default_factory=list)


class DecisionRequest(BaseModel):
    tenant_id: str
    optimization: OptimizationArtifact
    policy: PolicyResponse | None = None


class DecisionArtifact(BaseModel):
    decision_id: str
    tenant_id: str
    chosen_scenario_id: str | None = None
    rationale: str
    confidence: float
    scorecard: dict[str, float] = Field(default_factory=dict)


class ExplanationRequest(BaseModel):
    tenant_id: str
    decision: DecisionArtifact
    tone: str = "executive"


class ExplanationArtifact(BaseModel):
    tenant_id: str
    explanation_id: str
    text: str
    bullets: list[str] = Field(default_factory=list)


class ApprovalStage(BaseModel):
    stage_id: str
    name: str
    required_roles: list[str] = Field(default_factory=list)


class ApprovalRequest(BaseModel):
    tenant_id: str
    recommendation_id: str
    requested_by: str
    stages: list[ApprovalStage] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ApprovalTransitionRequest(BaseModel):
    approval_id: str
    actor_id: str
    actor_role: str
    action: Literal["approve", "reject"]
    reason: str | None = None


class ApprovalRecord(BaseModel):
    approval_id: str
    tenant_id: str
    recommendation_id: str
    requested_by: str
    status: Literal["PENDING", "APPROVED", "REJECTED"]
    current_stage_index: int = 0
    stages: list[ApprovalStage] = Field(default_factory=list)
    history: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    decided_by: str | None = None
    decided_reason: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OverrideRequest(BaseModel):
    tenant_id: str
    recommendation_id: str
    decision_id: str
    actor_id: str
    reason: str
    override_status: Literal["APPROVED", "REJECTED"]


class OverrideRecord(BaseModel):
    override_id: str
    tenant_id: str
    recommendation_id: str
    decision_id: str
    actor_id: str
    reason: str
    override_status: Literal["APPROVED", "REJECTED"]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ActionExecutionRequest(BaseModel):
    action_id: str
    tenant_id: str
    recommendation_id: str
    adapter_name: str
    payload: dict[str, Any] = Field(default_factory=dict)
    attempts: int = 1
    max_retries: int = 2
    async_mode: bool = False
    correlation_id: str | None = None


class ActionExecutionResult(BaseModel):
    action_id: str
    tenant_id: str
    recommendation_id: str
    adapter_name: str
    status: Literal["QUEUED", "SUCCEEDED", "FAILED"]
    attempts: int
    details: dict[str, Any] = Field(default_factory=dict)


class AuditEvent(BaseModel):
    event_id: str
    tenant_id: str
    correlation_id: str
    event_type: str
    resource_id: str
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ReplayRequest(BaseModel):
    tenant_id: str
    correlation_id: str | None = None
    resource_id: str | None = None


class ReplayArtifact(BaseModel):
    tenant_id: str
    events: list[AuditEvent] = Field(default_factory=list)


class ModelRegistrationRequest(BaseModel):
    model_id: str
    name: str
    version: str
    config: dict[str, Any] = Field(default_factory=dict)
    status: Literal["DRAFT", "ACTIVE", "INACTIVE"] = "DRAFT"


class ModelMetadata(BaseModel):
    model_id: str
    name: str
    version: str
    config: dict[str, Any] = Field(default_factory=dict)
    status: Literal["DRAFT", "ACTIVE", "INACTIVE"] = "DRAFT"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LearningTelemetry(BaseModel):
    outcome_id: str
    tenant_id: str
    recommendation_id: str
    decision_id: str
    outcome: Literal["SUCCESS", "FAILURE", "PARTIAL"]
    metrics: dict[str, float] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LearningRecord(BaseModel):
    learning_id: str
    tenant_id: str
    recommendation_id: str
    decision_id: str
    signal: float
    notes: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
