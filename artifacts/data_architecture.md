# CCC/ASE Data Architecture (Logical + Service Schemas)

This document defines the CCC/ASE data architecture and the minimum necessary schemas across services to support:

- multi-domain ingestion and canonicalization
- enterprise knowledge graph (causal + confidence-aware)
- scenario simulation and optimization
- Standard Decision Artifact (SDA) decisioning
- immutable audit/ledger and replay
- governed learning and model/policy versioning

Primary references:

- `solution.md`
- `detailed_requirements.md`
- `decision_standards.md`
- `api_contracts.md` (frozen payload schemas)
- `architecture.md`

## 1. Data Architecture Principles (Locked)

DA-001: **One canonical business language.** Raw sources remain authoritative, but CCC/ASE must normalize to a shared canonical model.

DA-002: **Event and artifact IDs everywhere.** Every major object must have stable IDs and be referenceable via artifacts for replay.

DA-003: **Append-only audit lineage.** Recommendation history must be immutable; mutations are new entries, not edits.

DA-004: **Tenant + domain partitioning.** All stored data must be partitionable by `tenant_id` and enforce domain/geography constraints.

DA-005: **Schema versioning.** Every key payload/table/graph element must carry `schema_version` or `version` with backward compatible evolution rules.

DA-006: **Governed learning.** Learning outputs are versioned, evaluated, promoted, and linked to decisions.

## 2. Storage Layers and Ownership

| Layer | Store Type | Purpose | Primary Writers | Primary Readers |
|---|---|---|---|---|
| Raw Landing | Object store (ADLS) | Immutable raw extracts/events/documents | Connector/Batch/Stream/Doc Parsing | Normalization, audit forensics |
| Curated Lakehouse | Analytical store | Canonical events, dimensions, KPIs | Normalization + MDM | Feature builder, simulation, analytics |
| Feature Store | KV + analytical | Derived features for event detection/sim/opt | Feature Builder | Event detection, simulation, optimization |
| Graph Store | Property graph | EKG: entities/edges, causal hypotheses | Graph Construction + Entity Resolution | Causal Reasoning, UI drill-down |
| Scenario Store | Doc/relational + artifacts | Scenario definitions and run results | Scenario Service | Optimizer, Decisioning, replay |
| Decision Store | Doc/relational | SDA snapshots, recommendation records | Decisioning, Governance | UI, execution |
| Decision Ledger | Append-only log + artifacts | Immutable lineage, replay pack, promotions | Ledger API + Governance + Learning | Replay, audit, compliance |
| Search Index | Index/vector | Evidence and artifact discovery | Explanation/Search pipeline | UI, analysts |
| Cache | Redis | Hot recommendations/paths | APIs | UI |

## 3. Cross-Cutting Data Controls

### 3.1 Partition Keys (Required)

Every persisted record MUST include:

- `tenant_id` (string)
- `business_unit_id` (string, optional but recommended)
- `geo_id` (string, optional but recommended)
- `domain` (`finance|hr|operations|it|cross_domain`)
- `ts` or `effective_ts` (ISO-8601 UTC) where time applies

### 3.2 Data Classification and Redaction

Each record SHOULD include:

- `data_classification`: `public|internal|confidential|restricted`
- `pii_present`: `true|false`
- `redaction_policy_id`: reference to policy set

### 3.3 Provenance (Required)

All derived objects MUST carry provenance linking back to:

- source systems and source record IDs (when available)
- ingestion job ID / event ID
- transformation lineage (pipeline/service version)

## 4. Canonical Domain Model (Curated Lakehouse)

This section defines the canonical entities (relational/doc representation) used for conformance and analytics.

### 4.1 Core Entities (Minimum Set)

All entities include common fields:

- `id` (canonical ID; stable)
- `tenant_id`, `business_unit_id`, `geo_id`, `domain`
- `source_refs[]` (source system + source keys)
- `valid_from_ts`, `valid_to_ts` (temporal validity when applicable)
- `last_updated_ts`

#### 4.1.1 Organization and People

- `OrgUnit`:
  - `org_unit_id`, `name`, `parent_org_unit_id`
- `Team`:
  - `team_id`, `org_unit_id`, `service_line_id`, `manager_person_id`
- `Person`:
  - `person_id`, `team_id`, `role_id`, `location_id`, `employment_status`, `criticality_tier`
- `Role`:
  - `role_id`, `role_family`, `level`, `critical_role_flag`
- `Skill`:
  - `skill_id`, `name`, `taxonomy_version`
- `PersonSkill` (bridge):
  - `person_id`, `skill_id`, `proficiency`, `last_validated_ts`

#### 4.1.2 Finance and Spend

- `CostCenter`:
  - `cost_center_id`, `name`, `owner_org_unit_id`
- `Vendor`:
  - `vendor_id`, `name`, `contract_end_ts`, `concentration_risk_score`
- `SpendFact` (time series):
  - `ts`, `cost_center_id`, `vendor_id`, `amount`, `currency`, `category`, `scenario_tag` (optional)

#### 4.1.3 Operations and Delivery

- `Service`:
  - `service_id`, `name`, `service_owner_team_id`
- `Platform`:
  - `platform_id`, `name`, `platform_owner_team_id`
- `SlaMetricFact` (time series):
  - `ts`, `service_id`, `metric_name`, `value`, `units`, `breach_risk_score`
- `ProcessMetricFact` (time series):
  - `ts`, `process_id`, `cycle_time`, `throughput`, `rework_rate`

#### 4.1.4 External Signals

- `ExternalSignal`:
  - `external_signal_id`, `name`, `signal_type`, `trust_tier`, `observed_ts`, `value`, `units`, `geo_id`

### 4.2 Canonical Signal Event (Normalized Event Envelope)

All streaming and batch “events” should be conformed to this canonical schema in the curated layer:

```json
{
  "schema_version": "1.0",
  "event_id": "string",
  "event_type": "string",
  "tenant_id": "string",
  "domain": "finance|hr|operations|it|cross_domain",
  "ts": "2026-04-18T12:34:56Z",
  "entity_refs": [{ "entity_id": "ent_123", "entity_type": "team", "name": "string" }],
  "payload_ref": { "uri": "string", "content_type": "application/json", "hash": "string" },
  "provenance": {
    "source_system": "string",
    "source_record_id": "string",
    "ingestion_job_id": "string"
  }
}
```

## 5. Feature Store Schema (Derived Signals)

### 5.1 Feature Definition (Registry)

```json
{
  "schema_version": "1.0",
  "feature_name": "string",
  "feature_version": "string",
  "entity_type": "team|org_unit|service|platform|cost_center|vendor|geo|other",
  "value_type": "number|string|boolean",
  "units": "string",
  "definition": "string",
  "source_inputs": ["string"],
  "freshness_slo_minutes": 1440
}
```

### 5.2 Feature Value (Online/Offline)

```json
{
  "schema_version": "1.0",
  "tenant_id": "string",
  "entity_id": "ent_123",
  "feature_name": "string",
  "feature_version": "string",
  "ts": "2026-04-18T12:34:56Z",
  "value": 0.23,
  "provenance_ref": "string"
}
```

## 6. Enterprise Knowledge Graph Schema (EKG)

### 6.1 Node Types (Minimum Set)

- `Person`, `Team`, `OrgUnit`, `Service`, `Platform`, `CostCenter`, `Vendor`, `Program`, `ExternalSignal`, `PolicyConstraint`, `Decision`

Node properties (minimum):

- `node_id`, `node_type`
- `tenant_id`, `domain`, `geo_id` (where applicable)
- `valid_from_ts`, `valid_to_ts` (temporal)
- `source_refs[]`
- `last_updated_ts`

### 6.2 Edge Types and Properties

Edges MUST support evidence classification (DS-002) and confidence.

Edge properties (minimum):

- `edge_id`
- `from_node_id`, `to_node_id`, `relationship_type`
- `direction` (if applicable)
- `evidence_class`: `confirmed_causal|probable_causal|correlated_only|expert_defined_rule|statistically_supported_link|inferred_dependency`
- `confidence` (`0.0..1.0`)
- `basis` (short basis string or artifact reference)
- `valid_from_ts`, `valid_to_ts`
- `source_refs[]`

### 6.3 Causal Hypothesis Object (Graph-Linked)

```json
{
  "schema_version": "1.0",
  "hypothesis_id": "string",
  "tenant_id": "string",
  "statement": "string",
  "status": "proposed|validated|deprecated",
  "primary_edge_id": "edge_123",
  "supporting_evidence_ids": ["ev_001"],
  "confidence": 0.68,
  "last_reviewed_ts": "2026-04-18T00:00:00Z",
  "owner_group": "string"
}
```

## 7. Scenario Store Schemas

Scenario contracts MUST align to `api_contracts.md`.

### 7.1 Scenario Definition (Storage View)

- corresponds to API: `Scenario Definition (Frozen v1.0)`
- persisted as:
  - `ScenarioHeader` (identity, scope, baseline_ref)
  - `ScenarioAssumptions[]`
  - `ScenarioConstraints[]`

### 7.2 Scenario Run (Storage View)

- `ScenarioRun`:
  - `scenario_run_id`, `scenario_id`, `status`, `mode`, `started_ts`, `completed_ts`
  - `inputs_artifact_ref`
  - `outputs[]` (metric + uncertainty)
  - `sensitivity_artifact_ref`

## 8. Optimization Schemas

### 8.1 Objective and Constraint Sets

```json
{
  "schema_version": "1.0",
  "weight_set_id": "string",
  "objectives": [{ "name": "Cost", "weight": 0.35 }],
  "constraints": {
    "hard": [{ "name": "BudgetCap", "operator": "<=", "value": 250000, "units": "USD" }],
    "soft": [{ "name": "SustainabilityScoreMin", "operator": ">=", "value": 3, "units": "score_1_5" }]
  }
}
```

### 8.2 Candidate Option

```json
{
  "schema_version": "1.0",
  "option_id": "opt_001",
  "label": "string",
  "interventions": [{ "type": "string", "parameters": {} }],
  "expected_effects_ref": "art_123"
}
```

### 8.3 Pareto Frontier Artifact (Reference)

Stored as an `artifact` with:

- option list
- scorecard deltas per option
- constraint satisfaction status
- stability diagnostics (optional)

## 9. Decisioning Data (SDA + Recommendation)

Decisioning contracts MUST align to `api_contracts.md` SDA and to `decision_standards.md`.

### 9.1 Recommendation Header (Relational/Document)

- `recommendation_id`, `decision_id`, `tenant_id`, `status`, `urgency`
- `created_ts`, `updated_ts`
- `current_sda_artifact_ref` (points to the SDA snapshot used for UI)

### 9.2 SDA Snapshot (Artifact)

Persist each SDA as an immutable artifact (`art_*`) and reference it from the ledger and recommendation header.

### 9.3 Evidence Pack (Artifact)

Persist `evidence_pack` as an immutable artifact, including:

- `items[]` (provenance + evidence class + confidence + references)
- `counterevidence[]`

### 9.4 Scorecard (Structured + Artifact)

Store scorecard as structured rows for query + an artifact for replay packaging:

- Dimension name
- `delta_score (-5..+5)`
- `risk_score (1..5)`
- `delta_estimate` + `uncertainty`
- `driver_reference_set[]`

### 9.5 Confidence Object

Store:

- component confidences
- overall confidence and band
- degradation reasons
- calibration status

## 10. Override Schemas

Override contracts MUST align to `api_contracts.md` and `decision_standards.md` DS-073/074.

Storage view:

- `OverrideHeader`: `override_id`, `recommendation_id`, `decision_id`, `override_type`, `reason_code`, `actor`, `ts`
- `OverrideChanges`:
  - objectives_delta[]
  - constraints_delta[]
  - assumptions_delta[]
- `RecomputeChain`:
  - links to recomputed scenario runs, optimization artifacts, and new SDA snapshot

## 11. Audit and Ledger Schemas

### 11.1 Audit Trace (Event Log)

Persist audit events as an append-only event log and expose via `audit_trace_id`.

- `event_id`, `event_type`, `ts`, `actor`, `correlation_id`
- `resource_refs[]` and `artifact_refs[]`

### 11.2 Decision Ledger (Append-Only)

Ledger entry types (minimum):

- `sda_snapshot`
- `override_snapshot`
- `policy_check`
- `execution_update`
- `learning_promotion`

Each entry MUST include:

- `ledger_entry_id`, `audit_trace_id`, `ts`
- `decision_id`, `recommendation_id`
- `payload_ref` (artifact reference)
- `versioning[]`

## 12. Service-Level Schema Contracts (Inputs/Outputs)

This section states the minimum I/O contracts per service boundary.

### 12.1 Semantic Normalization Service

Inputs:

- raw extracts/events (raw landing zone)

Outputs:

- canonical signal events (Section 4.2)
- canonical entity tables (Section 4.1)

### 12.2 MDM / Entity Resolution Service

Inputs:

- canonical entity tables

Outputs:

- identity linkage records
- graph node linkage updates (node merges/survivorship)

### 12.3 Knowledge Graph Service

Inputs:

- canonical entities + relationship candidates
- identity link updates

Outputs:

- nodes/edges with evidence class + confidence (Section 6)
- causal hypothesis objects (Section 6.3)

### 12.4 Signal Intelligence Service

Inputs:

- curated facts + graph state

Outputs:

- features (Section 5)
- detected events: trigger artifacts that start SDA cycles

### 12.5 Scenario Simulation Service

Inputs:

- Scenario Definition (Section 7.1)
- features + graph context

Outputs:

- Scenario Run Result (Section 7.2)
- sensitivity artifact

### 12.6 Optimization Service

Inputs:

- scenario runs + objectives + constraints

Outputs:

- pareto frontier artifact + selected option

### 12.7 Decisioning Service

Inputs:

- trigger event + evidence pack + scenarios + optimizer outputs

Outputs:

- SDA snapshot artifact (Section 9.2)
- recommendation header update (Section 9.1)

### 12.8 Explanation Service

Inputs:

- SDA snapshot artifact

Outputs:

- executive card and drill-down artifacts (explanation pack)
- search indexing payloads

### 12.9 Governance / Audit Service

Inputs:

- SDA snapshot and override objects

Outputs:

- policy check report artifact
- ledger entries (Section 11)

### 12.10 Learning Service

Inputs:

- outcome telemetry + audit events
- drift indicators

Outputs:

- new model/policy versions
- calibration artifacts
- ledger entries `learning_promotion`

## 13. Retention and Immutability (Minimum Guidance)

- Raw landing zone: retention per enterprise policy; immutable.
- Decision Ledger: long retention (years) for audit/replay; immutable by design.
- Scenario runs: retain per operational needs; minimum to support replay windows.
- Feature values: retain per training and backtesting horizon.

## 14. Open Items (Explicitly Deferred)

- Exact physical schemas per storage technology (SQL vs Cosmos vs lakehouse table formats).
- Final graph schema implementation details (Gremlin schema conventions, indexing).
- Full ABAC attribute model for domain/geography data access.

