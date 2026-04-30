# Cognitive Command Center (CCC) / Autonomous Strategy Engine (ASE) - API Contracts (Frozen v1)

## 1. Purpose

This document freezes the canonical, versioned API contracts for the CCC/ASE platform, with emphasis on:

- `recommendation` (Standard Decision Artifact + recommendation resource)
- `scenario` (definition + run + outputs)
- `override` (structured override inputs + recomputation)
- `audit` (decision ledger, events, replay)

Goals:

- enable parallel implementation across UI, agent services, and integrations without ambiguity
- ensure all contracts comply with `decision_standards.md` (confidence, causal evidence, scorecards, override rules)
- ensure auditability and replay are first-class

Non-goals:

- storage schemas (data plane) are not specified here
- infrastructure and security runbooks are not specified here

## 2. Conventions (Locked)

### 2.1 API Versioning

- All endpoints use URL prefix: `/api/v1/...`
- Backward-incompatible changes require `/api/v2/...`
- All primary payloads include `schema_version` (semantic version) independent of API version

### 2.2 Authentication and Authorization

- OAuth2/OIDC via Microsoft Entra ID
- HTTPS only
- Authorization: RBAC with optional ABAC (domain/geography/business unit)
- Every response MUST enforce tenant scoping and redaction policy

### 2.3 Idempotency and Correlation

- `Idempotency-Key` header is REQUIRED for all `POST` endpoints that create or mutate state
- `X-Correlation-Id` header is RECOMMENDED; echoed in responses
- All mutation endpoints MUST return `audit_trace_id`

### 2.4 Time, Currency, Units

- Time: ISO-8601 UTC (e.g., `2026-04-18T12:34:56Z`)
- Currency: ISO-4217 (e.g., `USD`, `INR`)
- Units must be explicit (e.g., `percent`, `FTE`, `hours`, `usd_monthly`)

### 2.5 Identifier Prefixes (Locked)

- `recommendation_id`: `rec_...`
- `decision_id`: `dec_...` (SDA id; stable across recompute chain)
- `scenario_id`: `scn_...`
- `scenario_run_id`: `run_...`
- `override_id`: `ovr_...`
- `audit_trace_id`: `trace_...`
- `ledger_entry_id`: `led_...`
- `artifact_id`: `art_...` (evidence pack, explanation pack, sensitivity report, etc.)
- `entity_id`: `ent_...`
- `edge_id`: `edge_...`

### 2.6 Numeric Ranges

- Confidence values use `0.0..1.0`
- Scorecard `delta_score` uses `-5..+5`
- Scorecard `risk_score` uses `1..5`

### 2.7 Standard Error Model (Locked)

All error responses MUST match:

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": [{ "field": "string", "issue": "string" }],
    "correlation_id": "string"
  }
}
```

Common `error.code` values:

- `AUTH_REQUIRED`
- `FORBIDDEN`
- `NOT_FOUND`
- `VALIDATION_ERROR`
- `CONFLICT`
- `RATE_LIMITED`
- `DEPENDENCY_UNAVAILABLE`
- `RECOMPUTE_IN_PROGRESS`

## 3. Shared Types (Frozen v1)

### 3.1 Actor

```json
{
  "actor_id": "string",
  "actor_type": "user|service",
  "display_name": "string",
  "role": "string"
}
```

### 3.2 Entity Reference

```json
{
  "entity_id": "ent_123",
  "entity_type": "person|team|org_unit|service|platform|cost_center|program|vendor|market_factor|other",
  "name": "string"
}
```

### 3.3 Artifact Reference

```json
{
  "artifact_id": "art_123",
  "artifact_type": "evidence_pack|explanation_pack|sensitivity_report|pareto_frontier|policy_check_report|other",
  "content_type": "application/json",
  "uri": "string",
  "hash": "string"
}
```

### 3.4 Version Reference

```json
{
  "kind": "model|policy|tool|dataset",
  "name": "string",
  "version": "string"
}
```

## 4. Frozen Schemas (v1)

This section freezes the payload schemas. Fields marked REQUIRED must be present.

### 4.1 Standard Decision Artifact (SDA) (Frozen v1.0)

The SDA is the source-of-truth for decisioning (DS-001, DS-010..DS-027).

```json
{
  "schema_version": "1.0",

  "decision_id": "dec_123",
  "recommendation_id": "rec_123",
  "audit_trace_id": "trace_123",

  "created_ts": "2026-04-18T12:34:56Z",
  "created_by": { "actor_id": "string", "actor_type": "user", "display_name": "string", "role": "string" },

  "trigger": {
    "trigger_type": "event|analyst_request|scheduled",
    "trigger_id": "string",
    "severity": "low|medium|high|critical",
    "trigger_confidence": 0.78
  },

  "scope": {
    "tenant_id": "string",
    "business_unit_id": "string",
    "geo_id": "string",
    "time_horizon": { "start_ts": "2026-04-18T00:00:00Z", "end_ts": "2026-07-18T00:00:00Z" },
    "entities": [
      { "entity_id": "ent_123", "entity_type": "team", "name": "Payments Ops - BLR" }
    ],
    "domain": "finance|hr|operations|it|cross_domain"
  },

  "objectives": {
    "weight_set_id": "string",
    "items": [
      { "name": "Cost", "weight": 0.35 },
      { "name": "TalentRetention", "weight": 0.35 },
      { "name": "DeliveryResilience", "weight": 0.30 }
    ]
  },

  "constraints": {
    "policy_set_id": "string",
    "hard": [
      { "name": "BudgetCap", "operator": "<=", "value": 250000, "units": "USD", "source": "policy|user|system" }
    ],
    "soft": [
      { "name": "SustainabilityScoreMin", "operator": ">=", "value": 3, "units": "score_1_5", "source": "policy|user|system" }
    ]
  },

  "assumptions": [
    { "key": "HiringFreeze", "value": "false", "units": "bool", "source": "system|user" }
  ],

  "evidence_pack": {
    "evidence_pack_id": "art_001",
    "items": [
      {
        "evidence_id": "ev_001",
        "source_system": "Workday",
        "source_type": "hr",
        "observed_ts": "2026-04-18T11:00:00Z",
        "freshness": { "max_age_minutes": 1440, "age_minutes": 120 },
        "classification": "confirmed_causal|probable_causal|correlated_only|expert_defined_rule|statistically_supported_link|inferred_dependency",
        "confidence": 0.72,
        "entity_refs": [{ "entity_id": "ent_123", "entity_type": "team", "name": "Payments Ops - BLR" }],
        "graph_path_refs": [{ "path_id": "string", "weakest_edge_id": "edge_123" }],
        "uri": "string"
      }
    ],
    "counterevidence": [
      {
        "evidence_id": "ev_999",
        "summary": "string",
        "classification": "correlated_only",
        "confidence": 0.40
      }
    ]
  },

  "scenarios": {
    "scenario_id": "scn_123",
    "runs": [
      { "scenario_run_id": "run_001", "label": "baseline" },
      { "scenario_run_id": "run_002", "label": "intervention_A" }
    ]
  },

  "options": [
    { "option_id": "opt_001", "label": "do_nothing" },
    { "option_id": "opt_002", "label": "targeted_retention_bonus" }
  ],

  "optimization_result": {
    "pareto_frontier_artifact": { "artifact_id": "art_200", "artifact_type": "pareto_frontier", "content_type": "application/json", "uri": "string", "hash": "string" },
    "selected_option_id": "opt_002",
    "alternatives": [
      { "option_id": "opt_003", "delta_summary": "string" },
      { "option_id": "opt_004", "delta_summary": "string" }
    ]
  },

  "risk_impact_scorecard": {
    "dimensions": [
      {
        "name": "FinancialImpact",
        "delta_score": -1,
        "risk_score": 2,
        "baseline_value_reference": "run_001",
        "delta_estimate": { "value": -120000, "units": "USD" },
        "uncertainty": { "kind": "interval", "low": -180000, "high": -60000, "units": "USD" },
        "driver_reference_set": ["ev_001", "run_002"]
      }
    ]
  },

  "confidence": {
    "components": {
      "data_confidence": 0.78,
      "graph_confidence": 0.74,
      "simulation_confidence": 0.70,
      "optimization_confidence": 0.72,
      "governance_confidence": 0.90
    },
    "overall_confidence": 0.76,
    "band": "High|Medium|Low|VeryLow",
    "degradation_reasons": [
      { "code": "STALE_SOURCE", "message": "string" }
    ],
    "calibration": {
      "status": "uncalibrated|calibrating|calibrated",
      "last_calibrated_ts": "2026-04-01T00:00:00Z"
    }
  },

  "explanation": {
    "executive_summary": "string",
    "key_drivers": [
      { "rank": 1, "name": "string", "direction": "increase|decrease", "relative_weight": 0.24, "evidence_id": "ev_001" }
    ],
    "explanation_pack_artifact": { "artifact_id": "art_300", "artifact_type": "explanation_pack", "content_type": "application/json", "uri": "string", "hash": "string" }
  },

  "governance": {
    "policy_checks_artifact": { "artifact_id": "art_400", "artifact_type": "policy_check_report", "content_type": "application/json", "uri": "string", "hash": "string" },
    "required_approvals": [
      { "approval_type": "domain_owner", "domain": "hr" }
    ],
    "violations": [
      { "code": "string", "severity": "warning|blocking", "message": "string" }
    ]
  },

  "execution_plan": {
    "mode": "dry_run|execute",
    "targets": [
      { "system": "ServiceNow", "endpoint": "string", "action_type": "create_ticket" }
    ],
    "success_metrics": [
      { "metric": "AttritionRate", "target_delta": -0.02, "units": "percent" }
    ]
  },

  "versioning": {
    "items": [
      { "kind": "model", "name": "scenario_simulator", "version": "1.3.0" },
      { "kind": "policy", "name": "approval_policy", "version": "2.1" }
    ]
  }
}
```

### 4.2 Recommendation Resource (Frozen v1.0)

```json
{
  "schema_version": "1.0",
  "recommendation_id": "rec_123",
  "decision_id": "dec_123",
  "audit_trace_id": "trace_123",

  "status": "draft|ready_for_review|approved|overridden|rejected|executed|closed",
  "urgency": "low|medium|high|critical",
  "title": "string",

  "created_ts": "2026-04-18T12:34:56Z",
  "updated_ts": "2026-04-18T12:34:56Z",

  "sda": { "schema_version": "1.0" }
}
```

### 4.3 Scenario Definition (Frozen v1.0)

```json
{
  "schema_version": "1.0",
  "scenario_id": "scn_123",
  "audit_trace_id": "trace_123",

  "created_ts": "2026-04-18T12:34:56Z",
  "created_by": { "actor_id": "string", "actor_type": "user", "display_name": "string", "role": "string" },

  "scope": {
    "tenant_id": "string",
    "business_unit_id": "string",
    "geo_id": "string",
    "entities": [{ "entity_id": "ent_123", "entity_type": "team", "name": "string" }],
    "time_horizon": { "start_ts": "2026-04-18T00:00:00Z", "end_ts": "2026-07-18T00:00:00Z" }
  },

  "baseline_ref": {
    "baseline_type": "graph_snapshot|curated_fact_set|recommendation_ref",
    "baseline_id": "string"
  },

  "assumptions": [
    { "key": "string", "value": "string", "units": "string", "source": "system|user" }
  ],

  "constraints": {
    "hard": [{ "name": "string", "operator": "<=|>=|=|!=|in", "value": "string", "units": "string" }],
    "soft": [{ "name": "string", "operator": "<=|>=|=|!=|in", "value": "string", "units": "string" }]
  }
}
```

### 4.4 Scenario Run Result (Frozen v1.0)

```json
{
  "schema_version": "1.0",
  "scenario_id": "scn_123",
  "scenario_run_id": "run_001",
  "audit_trace_id": "trace_123",

  "status": "queued|running|completed|failed",
  "mode": "event_triggered|analyst_ad_hoc|scheduled|recompute",
  "started_ts": "2026-04-18T12:34:56Z",
  "completed_ts": "2026-04-18T12:36:56Z",

  "inputs_ref": { "artifact_id": "art_501", "artifact_type": "other", "content_type": "application/json", "uri": "string", "hash": "string" },

  "outputs": [
    {
      "metric": "AttritionRate",
      "units": "percent",
      "estimate": { "value": 0.12, "units": "percent" },
      "uncertainty": { "kind": "interval", "low": 0.10, "high": 0.14, "units": "percent" }
    }
  ],

  "sensitivity": {
    "top_drivers": [
      { "rank": 1, "name": "string", "direction": "increase|decrease", "relative_weight": 0.31, "evidence_id": "ev_001" }
    ],
    "artifact_ref": { "artifact_id": "art_550", "artifact_type": "sensitivity_report", "content_type": "application/json", "uri": "string", "hash": "string" }
  }
}
```

### 4.5 Override Request / Record (Frozen v1.0)

Override types and reason codes MUST match `decision_standards.md` (DS-073/074).

```json
{
  "schema_version": "1.0",
  "override_id": "ovr_123",
  "recommendation_id": "rec_123",
  "decision_id": "dec_123",
  "audit_trace_id": "trace_123",

  "override_type": "AdjustObjectiveWeights|AddConstraint|RemoveConstraint|AdjustConstraintThreshold|ChangeAssumption|ChangeTimeHorizon|BlockAction|ForceAction|RequestMoreEvidence",
  "reason_code": "REGULATORY_OR_COMPLIANCE|BUDGET_LOCK_OR_FREEZE|TALENT_CRITICALITY|CUSTOMER_COMMITMENT|RISK_APPETITE_CHANGE|DATA_QUALITY_CONCERN|MODEL_MISMATCH_SUSPECTED|EXECUTIVE_DIRECTIVE|TIMELINE_CONSTRAINT|OTHER",
  "justification": "string",

  "actor": { "actor_id": "string", "actor_type": "user", "display_name": "string", "role": "string" },
  "created_ts": "2026-04-18T12:34:56Z",

  "changes": {
    "objectives_delta": [{ "name": "Cost", "weight": 0.40 }],
    "constraints_delta": [{ "name": "BudgetCap", "operator": "<=", "value": 200000, "units": "USD" }],
    "assumptions_delta": [{ "key": "HiringFreeze", "value": "true", "units": "bool" }]
  },

  "requires_governance_stamp": true,
  "human_directed": false
}
```

## 5. Audit, Ledger, and Replay Schemas (Frozen v1)

### 5.1 Audit Event (Frozen v1.0)

```json
{
  "schema_version": "1.0",
  "audit_trace_id": "trace_123",
  "event_id": "string",
  "event_type": "recommendation.created|recommendation.updated|recommendation.approved|recommendation.overridden|recommendation.recomputed|scenario.created|scenario.run_requested|scenario.run_completed|execution.dispatched|execution.completed|learning.promoted",
  "ts": "2026-04-18T12:34:56Z",
  "actor": { "actor_id": "string", "actor_type": "user|service", "display_name": "string", "role": "string" },
  "correlation_id": "string",
  "resource_refs": [
    { "kind": "recommendation", "id": "rec_123" },
    { "kind": "decision", "id": "dec_123" }
  ],
  "artifact_refs": [
    { "artifact_id": "art_123", "artifact_type": "evidence_pack", "content_type": "application/json", "uri": "string", "hash": "string" }
  ],
  "summary": "string",
  "details": {}
}
```

### 5.2 Ledger Entry (Frozen v1.0)

Ledger entries are append-only and replayable (DS-080/081).

```json
{
  "schema_version": "1.0",
  "ledger_entry_id": "led_123",
  "audit_trace_id": "trace_123",
  "ts": "2026-04-18T12:34:56Z",

  "decision_id": "dec_123",
  "recommendation_id": "rec_123",

  "entry_type": "sda_snapshot|override_snapshot|policy_check|execution_update|learning_promotion",
  "payload_ref": { "artifact_id": "art_900", "artifact_type": "other", "content_type": "application/json", "uri": "string", "hash": "string" },

  "versioning": [{ "kind": "policy", "name": "approval_policy", "version": "2.1" }]
}
```

### 5.3 Replay Response (Frozen v1.0)

```json
{
  "schema_version": "1.0",
  "recommendation_id": "rec_123",
  "decision_id": "dec_123",
  "as_of_ts": "2026-04-18T12:34:56Z",
  "replay_status": "ready|building|failed",
  "inputs": {
    "graph_snapshot_ref": "string",
    "scenario_run_ids": ["run_001", "run_002"],
    "versioning": [{ "kind": "model", "name": "scenario_simulator", "version": "1.3.0" }]
  },
  "sda": { "schema_version": "1.0" }
}
```

## 6. Core APIs (Frozen v1)

### 6.1 Create Recommendation (Decision Cycle)

`POST /api/v1/recommendations`

Headers:

- `Idempotency-Key: <uuid>`

Body (minimal trigger + scope; server builds SDA):

```json
{
  "schema_version": "1.0",
  "trigger": { "trigger_type": "event|analyst_request|scheduled", "trigger_id": "string" },
  "scope": {
    "tenant_id": "string",
    "business_unit_id": "string",
    "geo_id": "string",
    "domain": "finance|hr|operations|it|cross_domain",
    "entities": [{ "entity_id": "ent_123", "entity_type": "team", "name": "string" }]
  },
  "objectives": { "items": [{ "name": "Cost", "weight": 0.4 }] },
  "constraints": { "hard": [], "soft": [] },
  "assumptions": []
}
```

Response:

```json
{
  "recommendation_id": "rec_123",
  "decision_id": "dec_123",
  "status": "draft",
  "audit_trace_id": "trace_123"
}
```

### 6.2 Get Recommendation

`GET /api/v1/recommendations/{recommendation_id}`

Response: Recommendation Resource with embedded SDA (Sections 4.1 and 4.2).

### 6.3 Approve Recommendation

`POST /api/v1/recommendations/{recommendation_id}/approve`

Headers:

- `Idempotency-Key: <uuid>`

Body:

```json
{ "schema_version": "1.0", "approval_notes": "string" }
```

Response:

```json
{ "recommendation_id": "rec_123", "status": "approved", "audit_trace_id": "trace_123" }
```

### 6.4 Override Recommendation (Triggers Recompute)

`POST /api/v1/recommendations/{recommendation_id}/override`

Headers:

- `Idempotency-Key: <uuid>`

Body: Override Record (Section 4.5) with `changes`.

Response:

```json
{
  "override_id": "ovr_123",
  "recommendation_id": "rec_123",
  "status": "overridden",
  "recompute_status": "queued|running|completed",
  "audit_trace_id": "trace_123"
}
```

### 6.5 Create Scenario

`POST /api/v1/scenarios`

Headers:

- `Idempotency-Key: <uuid>`

Body: Scenario Definition (Section 4.3).

Response:

```json
{ "scenario_id": "scn_123", "status": "draft", "audit_trace_id": "trace_123" }
```

### 6.6 Run Scenario

`POST /api/v1/scenarios/{scenario_id}/simulate`

Headers:

- `Idempotency-Key: <uuid>`

Body:

```json
{ "schema_version": "1.0", "mode": "event_triggered|analyst_ad_hoc|scheduled|recompute" }
```

Response:

```json
{ "scenario_id": "scn_123", "scenario_run_id": "run_001", "status": "running", "audit_trace_id": "trace_123" }
```

### 6.7 Get Scenario Run

`GET /api/v1/scenarios/{scenario_id}/runs/{scenario_run_id}`

Response: Scenario Run Result (Section 4.4).

### 6.8 Get Audit Trace

`GET /api/v1/audit/traces/{audit_trace_id}`

Response:

```json
{ "audit_trace_id": "trace_123", "events": [] }
```

### 6.9 Replay Recommendation

`GET /api/v1/replay/recommendations/{recommendation_id}?as_of_ts=2026-04-18T12:34:56Z`

Response: Replay Response (Section 5.3).

## 7. Event Envelope (Reference, Frozen v1)

All emitted events SHOULD use the following envelope (payload by reference):

```json
{
  "schema_version": "1.0",
  "event_id": "string",
  "event_type": "string",
  "ts": "2026-04-18T12:34:56Z",
  "tenant_id": "string",
  "correlation_id": "string",
  "payload_ref": { "artifact_id": "art_123", "artifact_type": "other", "content_type": "application/json", "uri": "string", "hash": "string" }
}
```

## 8. Open Items (Explicitly Deferred)

- Whether GraphQL is added for UI composition (REST-only assumed for v1).
- Final policy rules expression format (JSON rules vs DSL vs external engine).
- External market signal provider selection (licensing, refresh SLAs).

