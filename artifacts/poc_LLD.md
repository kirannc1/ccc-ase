# CCC / ASE Low-Level Design (PoC)

## 1. POC Scope Summary

The PoC must prove two end-to-end strategic decision journeys and one override/replay cycle:

- Journey 1: attrition spike in a critical delivery team, using engagement, absenteeism, backfill delay, and external offer-acceptance signals.
- Journey 2: cost pressure with demand uncertainty, using cloud cost drift, vendor inflation, and forecast uncertainty signals.
- Override demo: change assumptions or objective weights, recompute scenarios and optimization, and show before/after deltas with audit trace.

These journeys map to the following capabilities:

- multi-domain ingestion and canonicalization
- enterprise knowledge graph reasoning with causal evidence classification
- what-if scenario simulation and sensitivity analysis
- multi-objective optimization with constrained trade-offs
- structured recommendation generation through an SDA
- confidence breakdown, scorecards, and alternatives
- human override with recomputation
- immutable decision ledger, audit, and replay
- governed learning from outcomes and feedback

## 2. Service Decomposition

### 2.1 Service Catalog

| Service | Responsibility | Boundaries | Key APIs | Dependencies | State |
|---|---|---|---|---|---|
| API Gateway | Single external entry point, auth enforcement, routing, throttling | Owns API policy only; does not own business data | Public `/api/v1/*` and internal routing | Entra ID, APIM, cache, downstream services | Stateless |
| Identity and Access Proxy | Token validation, tenant scoping, role mapping, redaction context | Owns security context only | Auth middleware, token validation | Entra ID, Key Vault, APIM | Stateless |
| Source Connector Service | Manage source system registrations and pull/subscription connectors | Owns connector catalog only | Ingestion registration and health APIs | SQL metadata store, Event Hubs, Data Factory | Stateful |
| Batch Ingestion Service | Scheduled extracts, validation, raw landing writes | Owns batch run metadata only | Batch ingestion internal APIs | ADLS raw, SQL metadata, Event Hubs | Stateful |
| Streaming Ingestion Service | Near-real-time event validation and publishing | Owns stream checkpoint metadata only | Stream ingestion internal APIs | Event Hubs, ADLS raw, SQL metadata | Stateful |
| Document Parsing Service | OCR/extract structured facts from documents | Owns parsing jobs and extraction refs | Parsing internal APIs | ADLS raw, Event Hubs, SQL metadata | Stateful |
| Semantic Normalization Service | Canonicalize source fields into enterprise model | Owns normalization rules and canonical event writes | `/internal/normalize` | Curated lakehouse, Event Hubs, Entity Resolution | Stateful |
| Master Data and Entity Resolution Service | Survivorship, identity linkage, persistent enterprise IDs | Owns entity linkage and MDM rules | Entity resolution internal APIs | Curated lakehouse, graph service | Stateful |
| Knowledge Graph Service | Store entities, temporal edges, causal hypotheses, graph traversals | Owns graph state only | `GET /api/v1/graph/entities/{id}`, `GET /api/v1/graph/path`, `POST /api/v1/graph/query` | Graph DB, curated lakehouse, cache | Stateful |
| Signal Intelligence Service | Detect strategic events from curated facts and graph state | Owns event detection rules only | Internal event detection APIs | Feature store, KG, anomaly/forecast/causal services | Stateful |
| Feature Engineering Service | Build reusable features for detection, simulation, and optimization | Owns feature definitions and feature values | `/internal/features/generate` | Feature store, curated lakehouse, graph service | Stateful |
| Forecasting Model Service | Produce forecasts and uncertainty bands | Owns model inference versioning only | Internal forecast inference APIs | Feature store, AML, cache | Stateless |
| Anomaly Detection Service | Rank anomalies against expected baselines | Owns anomaly model config only | Internal anomaly scoring APIs | Feature store, curated lakehouse | Stateless |
| Causal Inference Service | Score cause-effect paths and annotate edges | Owns causal scoring outputs only | Internal causal scoring APIs | Graph service, curated lakehouse | Stateless |
| Scenario Simulation Service | Create and run what-if simulations and sensitivity analysis | Owns scenario runs and run outputs | `/api/v1/scenarios`, `/api/v1/scenarios/{id}/simulate`, `/api/v1/scenarios/{id}/compare`, `/api/v1/scenarios/{id}/runs/{run_id}` | Scenario store, feature store, graph service, policy service | Stateful |
| Policy and Constraint Service | Store business constraints and validation rules | Owns policies and constraints only | `/api/v1/policies` | SQL or document store, ledger | Stateful |
| Optimization Service | Rank alternatives, compute Pareto frontier, enforce constraints | Owns optimization runs only | Internal optimization run APIs | Scenario store, policy service, feature store | Stateful |
| Decisioning Service | Build SDA, recommendation record, confidence, scorecards | Owns recommendation lifecycle state | `/api/v1/recommendations`, `/api/v1/recommendations/{id}`, `/api/v1/recommendations/{id}/scorecard`, `/api/v1/recommendations/{id}/drivers`, `/api/v1/recommendations/{id}/confidence` | Decision store, ledger, optimization, scenarios, KG | Stateful |
| Explanation Service | Render executive and drill-down explanation packs | Owns explanation artifacts only | `/internal/explanation/render` | Search index, decision store, ledger, LLM orchestration | Stateless |
| LLM Orchestration Service | Controlled narrative generation from structured SDA | Owns prompts/templates and model routing only | Internal LLM request APIs | Azure OpenAI, prompt store, guardrails | Stateless |
| Approval Workflow Service | Review routing and approval chain management | Owns approval status only | `/api/v1/recommendations/{id}/approve`, review callbacks | Service Bus, decision store, ledger | Stateful |
| Human Override Service | Capture structured override and trigger recompute | Owns override records only | `/api/v1/recommendations/{id}/override`, `/api/v1/recommendations/{id}/override-comparison` | Service Bus, decisioning, scenarios, optimization | Stateful |
| Execution Orchestrator | Dispatch approved actions and track execution status | Owns execution workflow state only | Internal dispatch APIs | Service Bus, action adapters, telemetry | Stateful |
| Action Adapter Service | Translate approved actions into system-specific commands | Owns adapter configuration only | Internal action dispatch adapters | External enterprise systems | Stateless |
| Audit Trail Service | Persist immutable audit events | Owns audit event log only | `/api/v1/audit/traces/{audit_trace_id}` | Decision ledger, object store, APIM | Stateful |
| Recommendation Replay Service | Reconstruct recommendation as-of a point in time | Owns replay query state only | `/api/v1/replay/recommendations/{recommendation_id}` | Decision ledger, decision store, KG, scenario store | Stateless |
| Model Registry Service | Govern model versions, evaluation, and promotion | Owns registry and evaluation metadata | Internal registry APIs | Azure ML, ledger | Stateful |
| Learning Service | Ingest outcomes, feedback, drift and promote learning updates | Owns learning runs and promotion records | Internal learning APIs | Azure ML, telemetry, ledger, KG, scenario service | Stateful |
| Leadership Web App | Leadership decision workspace | UI composition only | Calls recommendation, scenario, replay APIs | APIM, cache, graph and decision APIs | Stateless |
| Strategy Ops Console | Analyst scenario lab and investigation UI | UI composition only | Calls graph, scenario, optimization, explanation APIs | APIM, cache, search | Stateless |
| Admin and Governance Console | Policy, audit, and model governance UI | UI composition only | Calls audit, policies, replay, registry APIs | APIM, ledger, AML | Stateless |

### 2.2 Inter-Dependency Order

Least dependency first:

1. API Gateway and Identity and Access Proxy
2. Source Connector, Batch Ingestion, Streaming Ingestion, Document Parsing
3. Semantic Normalization and Master Data / Entity Resolution
4. Feature Engineering
5. Knowledge Graph and Signal Intelligence
6. Forecasting, Anomaly Detection, and Causal Inference
7. Policy and Constraint Service
8. Scenario Simulation
9. Optimization
10. Decisioning and Explanation
11. Approval Workflow and Human Override
12. Execution Orchestrator and Action Adapters
13. Audit Trail and Recommendation Replay
14. Model Registry and Learning
15. Frontend apps

## 3. Database Design (Per Service)

### 3.1 Service-to-Store Mapping

| Service | Database Type | Primary Schemas / Collections | Keys and Indexes | Canonical Model Mapping |
|---|---|---|---|---|
| API Gateway | None | No business persistence | N/A | N/A |
| Identity and Access Proxy | None | No business persistence | N/A | N/A |
| Source Connector Service | SQL | `source_system`, `connector`, `connector_run`, `source_registration` | PKs on IDs; index by `tenant_id`, `source_system_id`, `status` | Operational metadata entities |
| Batch Ingestion Service | ADLS + SQL | Raw files in object store; `batch_job`, `batch_run`, `validation_result` | PK on run IDs; index by `tenant_id`, `job_status`, `run_ts` | Raw landing to canonical event envelope |
| Streaming Ingestion Service | ADLS + SQL | Raw event blobs; `stream_checkpoint`, `stream_batch` | PK on checkpoint IDs; index by `tenant_id`, `partition`, `offset` | Canonical signal event envelope |
| Document Parsing Service | ADLS + SQL | Parsed artifact blobs; `document_job`, `extraction_result` | PK on job IDs; index by `tenant_id`, `document_type`, `source_system` | External signal / document payloads |
| Semantic Normalization Service | Lakehouse | `canonical_event`, `org_unit`, `team`, `person`, `role`, `skill`, `person_skill`, `cost_center`, `vendor`, `service`, `platform`, `spend_fact`, `sla_metric_fact`, `process_metric_fact`, `external_signal` | PK on canonical IDs; partition by `tenant_id`, `domain`, date | Canonical domain model in `canonical_data_model_erd.puml` |
| Master Data and Entity Resolution Service | Lakehouse + SQL | `entity_match`, `entity_survivorship`, `identity_link`, `taxonomy_map` | PK on enterprise entity IDs; index by `source_system`, `match_status`, `tenant_id` | `Team`, `Person`, `Service`, `CostCenter`, `Vendor` |
| Feature Engineering Service | Feature store | `feature_def`, `feature_value`, `feature_snapshot` | PK on `(tenant_id, entity_id, feature_name, feature_version, ts)`; index by `entity_type`, `feature_name` | Derived signals from canonical entities |
| Knowledge Graph Service | Graph DB | Nodes: `person`, `team`, `service`, `platform`, `vendor`, `cost_center`, `external_signal`, `policy_constraint`, `decision`; edges: causal and dependency links; `causal_hypothesis` | Node key `node_id`; edge key `edge_id`; index by `tenant_id`, `node_type`, `relationship_type`, `valid_from_ts` | `knowledge_graph_schema.puml` and ERD node mappings |
| Signal Intelligence Service | Feature store + SQL | `signal_event`, `signal_alert`, `pattern_rule`, `event_trigger` | PK on event IDs; index by `tenant_id`, `severity`, `entity_id`, `ts` | Strategic events over canonical facts |
| Forecasting Model Service | Feature store / model registry | No separate operational tables beyond inference metadata | Index by `model_version`, `feature_set_id` | Forecast outputs link to scenarios |
| Anomaly Detection Service | Feature store / SQL | `anomaly_score`, `baseline_profile`, `anomaly_explanation` | Index by `tenant_id`, `entity_id`, `metric_name`, `ts` | Signal health and drift |
| Causal Inference Service | Graph DB + SQL | `causal_score`, `hypothesis_review`, `evidence_bundle` | Index by `edge_id`, `hypothesis_id`, `confidence` | Causal edges and hypothesis objects |
| Scenario Simulation Service | SQL / document store + object store | `scenario_header`, `scenario_assumption`, `scenario_constraint`, `scenario_run`, `scenario_output`, `sensitivity_result` | PK on scenario/run IDs; index by `tenant_id`, `status`, `mode`, `scenario_id` | Scenario store schemas from `data_architecture.md` |
| Policy and Constraint Service | SQL / document store | `policy`, `policy_version`, `constraint`, `constraint_set`, `approval_rule` | PK on policy IDs; index by `tenant_id`, `domain`, `effective_ts` | Policy constraints linked to SDA |
| Optimization Service | SQL / object store | `weight_set`, `candidate_option`, `pareto_frontier`, `optimization_run`, `objective_delta` | PK on run IDs; index by `tenant_id`, `scenario_run_id`, `selected_flag` | Optimization outputs linked to SDA and scenario runs |
| Decisioning Service | SQL / document store + object store | `recommendation_header`, `sda_snapshot_ref`, `confidence_record`, `scorecard_row`, `decision_option`, `decision_version` | PK on `decision_id`, `recommendation_id`; index by `tenant_id`, `status`, `created_ts` | SDA and recommendation resource in `api_contracts.md` |
| Explanation Service | Search index + object store | `explanation_pack`, `driver_index`, `evidence_index` | Index by `decision_id`, `evidence_id`, `entity_id`, `keyword` | `artifact_id` refs for explanation pack |
| LLM Orchestration Service | SQL | `prompt_template`, `prompt_version`, `model_call`, `redaction_rule` | Index by `model_name`, `prompt_name`, `version` | Narrative derived from SDA only |
| Approval Workflow Service | SQL | `approval_request`, `approval_step`, `approval_comment` | Index by `recommendation_id`, `approver_role`, `status` | Approval metadata only |
| Human Override Service | SQL + object store | `override_header`, `override_change`, `recompute_chain` | Index by `override_id`, `recommendation_id`, `reason_code` | Override storage view from `data_architecture.md` |
| Execution Orchestrator | SQL | `execution_request`, `execution_step`, `execution_status` | Index by `recommendation_id`, `system`, `status` | Execution lifecycle only |
| Action Adapter Service | None / external system | No persistent business schema | N/A | External execution endpoint adapters |
| Audit Trail Service | Append-only log + object store | `audit_event`, `audit_resource_ref`, `audit_artifact_ref` | Immutable append key on `event_id`; index by `audit_trace_id`, `ts`, `event_type` | Audit event schema from `api_contracts.md` |
| Recommendation Replay Service | Append-only ledger + object store | `ledger_entry`, replay manifests, immutable artifact refs | Immutable append key on `ledger_entry_id`; index by `decision_id`, `recommendation_id`, `ts`, `entry_type` | Decision ledger schema |
| Model Registry Service | Azure ML registry + SQL | `model_asset`, `evaluation_result`, `promotion_request`, `promotion_decision` | Index by `model_name`, `version`, `status` | Learning and version references |
| Learning Service | Azure ML + SQL + ledger | `outcome_telemetry`, `feedback_signal`, `drift_signal`, `promotion_record` | Index by `decision_id`, `model_version`, `promoted_flag`, `ts` | Governed learning lifecycle |

### 3.2 Canonical Model to Store Mapping

- `canonical_data_model_erd.puml`: raw-to-curated relational/lakehouse entities.
- `knowledge_graph_schema.puml`: graph nodes, edges, and causal hypotheses.
- `decision_lineage_data_model.puml`: SDA, recommendation, override, audit, and ledger records.

## 4. Messaging and Event Design

### 4.1 Messaging Backbone

- `Azure Event Hubs` for streaming events and detection triggers.
- `Azure Service Bus` for commands, approval workflow, and recompute requests.
- `Object storage` for immutable artifacts referenced from events.

### 4.2 Common Event Envelope

```json
{
  "schema_version": "1.0",
  "event_id": "evt_123",
  "event_type": "string",
  "tenant_id": "string",
  "domain": "finance|hr|operations|it|cross_domain",
  "ts": "2026-04-18T12:34:56Z",
  "correlation_id": "trace_123",
  "entity_refs": [],
  "artifact_refs": [],
  "provenance": {
    "source_system": "string",
    "source_record_id": "string",
    "ingestion_job_id": "string"
  },
  "payload_ref": {
    "uri": "string",
    "content_type": "application/json",
    "hash": "string"
  }
}
```

### 4.3 Topic and Queue Structure

| Topic / Queue | Producer | Consumer |
|---|---|---|
| `source.raw.received` | Source connectors, batch, stream, document parser | Normalization, audit |
| `source.batch.validated` | Batch ingestion | Normalization, metadata store |
| `source.stream.received` | Streaming ingestion | Signal intelligence, normalization |
| `canonical.event.created` | Semantic normalization | Entity resolution, feature engineering |
| `entity.resolution.completed` | Entity resolution | KG, signal intelligence |
| `graph.updated` | Knowledge graph | Causal reasoning, explanation |
| `strategic.event.detected` | Signal intelligence | Scenario simulation, decisioning |
| `scenario.requested` | Decisioning, UI, override flow | Scenario simulation |
| `scenario.completed` | Scenario simulation | Optimization, decisioning |
| `optimization.completed` | Optimization | Decisioning, explanation |
| `recommendation.created` | Decisioning | Approval workflow, audit, UI |
| `recommendation.approved` | Approval workflow | Execution orchestrator |
| `recommendation.overridden` | Human override | Decisioning, scenario simulation, optimization |
| `recommendation.recomputed` | Decisioning | UI, audit, replay |
| `execution.dispatched` | Execution orchestrator | Action adapters |
| `execution.completed` | Action adapters | Audit, learning |
| `feedback.received` | Execution, UI feedback, telemetry | Learning service |
| `learning.promoted` | Learning service | Model registry, ledger, KG updates |

### 4.4 Textual Event Flow

1. Source systems emit raw data or documents.
2. Ingestion services land raw payloads and publish validation events.
3. Normalization creates canonical events and entity resolution updates.
4. KG and feature services consume canonical data and emit derived state.
5. Signal intelligence raises strategic events.
6. Scenario simulation evaluates baseline and intervention cases.
7. Optimization ranks candidate options and writes the frontier.
8. Decisioning builds the SDA and recommendation record.
9. Explanation renders structured packs for the UI.
10. Approval workflow routes the recommendation.
11. Override requests trigger recomputation through the orchestrator.
12. Execution updates and outcome telemetry feed the learning loop.

## 5. API Layer Design

### 5.1 Frozen Public APIs

| Endpoint | Service | Purpose | Validation Rules | Errors |
|---|---|---|---|---|
| `POST /api/v1/recommendations` | Decisioning | Create a recommendation cycle | `Idempotency-Key` required, `schema_version` required, tenant scope required | Standard error model |
| `GET /api/v1/recommendations/{recommendation_id}` | Decisioning | Fetch recommendation + SDA reference | Tenant scoped, authenticated access | `NOT_FOUND`, `FORBIDDEN` |
| `POST /api/v1/recommendations/{recommendation_id}/approve` | Approval Workflow | Approve a recommendation | Approval role check, correlation ID echoed | `FORBIDDEN`, `CONFLICT` |
| `POST /api/v1/recommendations/{recommendation_id}/override` | Human Override | Capture override and recompute | Structured override type and reason code required | `VALIDATION_ERROR`, `RECOMPUTE_IN_PROGRESS` |
| `GET /api/v1/recommendations/{recommendation_id}/scorecard` | Decisioning | Return scorecard | Tenant scoped | `NOT_FOUND` |
| `GET /api/v1/recommendations/{recommendation_id}/drivers` | Explanation | Return ranked drivers | Tenant scoped | `NOT_FOUND` |
| `GET /api/v1/recommendations/{recommendation_id}/confidence` | Decisioning | Return confidence breakdown | Tenant scoped | `NOT_FOUND` |
| `POST /api/v1/scenarios` | Scenario Simulation | Create scenario definition | Baseline ref and assumptions required | `VALIDATION_ERROR` |
| `POST /api/v1/scenarios/{scenario_id}/simulate` | Scenario Simulation | Run scenario | Scenario exists, idempotent | `CONFLICT`, `DEPENDENCY_UNAVAILABLE` |
| `POST /api/v1/scenarios/{scenario_id}/compare` | Scenario Simulation | Compare scenarios | Scenario IDs required | `VALIDATION_ERROR` |
| `GET /api/v1/scenarios/{scenario_id}/runs/{scenario_run_id}` | Scenario Simulation | Fetch run result | Tenant scoped | `NOT_FOUND` |
| `GET /api/v1/scenarios/{scenario_id}/market-signals` | Scenario Simulation | Return external signals used | Tenant scoped | `NOT_FOUND` |
| `GET /api/v1/graph/entities/{id}` | Knowledge Graph | Entity details and relationships | Tenant scoped | `NOT_FOUND` |
| `GET /api/v1/graph/path` | Knowledge Graph | Causal path traversal | Source and target entity IDs required | `VALIDATION_ERROR` |
| `POST /api/v1/graph/query` | Knowledge Graph | Free-form graph query | Query validation and tenant scoping | `VALIDATION_ERROR` |
| `GET /api/v1/audit/traces/{audit_trace_id}` | Audit Trail | Return audit event stream | Audit trace exists | `NOT_FOUND` |
| `GET /api/v1/replay/recommendations/{recommendation_id}?as_of_ts=...` | Replay | Reconstruct recommendation as of a timestamp | `as_of_ts` required | `NOT_FOUND`, `VALIDATION_ERROR` |
| `GET /api/v1/policies` | Policy Service | List policies | Authenticated access only | `FORBIDDEN` |
| `POST /api/v1/policies` | Policy Service | Create/update policy version | Admin role only, `Idempotency-Key` required | `FORBIDDEN`, `CONFLICT` |
| `GET /api/v1/recommendations/{recommendation_id}/override-comparison` | Human Override | Before/after comparison | Tenant scoped | `NOT_FOUND` |

### 5.2 Internal API Contracts

- `POST /internal/normalize`
- `POST /internal/features/generate`
- `POST /internal/graph/update`
- `POST /internal/simulation/run`
- `POST /internal/optimization/run`
- `POST /internal/explanation/render`
- `POST /internal/actions/dispatch`

### 5.3 Request Validation Standards

- All mutation endpoints require `Idempotency-Key`.
- All requests require tenant scoping and role-based authorization.
- All responses must include correlation IDs and the standard error model from `api_contracts.md`.
- Confidence values must stay in `0.0..1.0`; scorecard deltas must stay in `-5..+5`.

## 6. UI Design (POC Level)

### 6.1 Required Screens

- Leadership Dashboard
- Scenario Lab
- Recommendation Detail and Override View
- Audit and Replay View
- Admin and Governance View

### 6.2 User Flows

1. Leadership sees strategic events and recommendation cards.
2. Strategy Ops opens a journey, inspects the graph path, and runs scenarios.
3. User reviews alternatives, scorecards, and confidence.
4. User applies an override, which triggers recomputation.
5. User reviews before/after deltas and audit trail.
6. Governance user reviews replay, policies, and learning promotion state.

### 6.3 API Integrations Per Screen

- Leadership Dashboard: recommendations, drivers, confidence, scorecard, audit summary.
- Scenario Lab: create scenario, run scenario, compare runs, market signals.
- Recommendation Detail: recommendation fetch, graph path, scenario runs, override, override comparison.
- Audit and Replay: audit trace, replay recommendation, ledger entries.
- Admin and Governance: policies, approval queues, model registry, learning promotions.

### 6.4 Minimal Component Hierarchy

- App shell
  - global navigation
  - tenant selector
  - role-aware action bar
- Leadership Dashboard
  - event summary cards
  - recommendation card
  - confidence widget
  - scorecard table
  - causal path viewer
- Scenario Lab
  - baseline selector
  - assumptions editor
  - scenario run timeline
  - sensitivity chart
- Audit and Replay
  - trace timeline
  - artifact list
  - replay comparison panel

### 6.5 State Management

- Server state: React Query or equivalent data-fetching cache.
- Local UI state: form state, selection state, and view mode state.
- Long-running jobs: poll or subscribe to run status updates.
- Shared UI context: tenant, role, correlation ID, and current decision cycle.

## 7. Order of Development

### 7.1 Foundation

1. Set up Azure landing zones, subscriptions, identity, APIM, ACR, Key Vault, monitoring, AKS, ADLS, SQL, Cosmos, graph, search, Redis, Event Hubs, Service Bus, and AML.
2. Create repository structure, IaC, CI/CD, and shared contract packages.
3. Freeze schemas and API request/response models.

Dependencies:

- Infrastructure and secrets must exist before services can be deployed.
- API and data contracts must be frozen before service implementation starts.

Parallelization:

- Infra and contract work can proceed in parallel.
- UI shell can begin once API shapes are frozen.

### 7.2 Core Services

1. Source Connector, Batch Ingestion, Streaming Ingestion, and Document Parsing.
2. Semantic Normalization and Entity Resolution.
3. Feature Engineering and Knowledge Graph.

Dependencies:

- Raw ingestion must exist before normalization.
- Normalization and entity resolution must exist before KG and feature generation.

Parallelization:

- Batch, streaming, and document ingestion can be built in parallel.
- KG and feature store can be implemented alongside entity resolution once canonical schemas are agreed.

### 7.3 Supporting Intelligence Services

1. Signal Intelligence.
2. Forecasting, Anomaly Detection, and Causal Inference.
3. Policy and Constraint Service.

Dependencies:

- These services depend on canonical data, graph state, and feature definitions.

Parallelization:

- Forecasting, anomaly, and causal scoring can be parallelized because they share features but have separate runtime paths.

### 7.4 Decision Services

1. Scenario Simulation.
2. Optimization.
3. Decisioning.
4. Explanation and LLM Orchestration.

Dependencies:

- Scenario simulation depends on features, graph context, and policy constraints.
- Optimization depends on scenario outputs.
- Decisioning depends on scenario and optimization artifacts.
- Explanation depends on the SDA and search artifacts.

Parallelization:

- Scenario simulation and policy service can be built together.
- Explanation can be prototyped once SDA fields are frozen.

### 7.5 Workflow, Governance, and Learning

1. Approval Workflow.
2. Human Override.
3. Execution Orchestrator and Action Adapters.
4. Audit Trail and Replay.
5. Model Registry and Learning Service.

Dependencies:

- These services depend on recommendation artifacts and immutable IDs.
- Learning depends on outcome telemetry and audit data.

Parallelization:

- Audit/replay and learning can be built once the ledger schema is defined.
- Execution adapters can be stubbed during the PoC.

### 7.6 UI

1. Leadership Dashboard and Scenario Lab.
2. Recommendation Detail and Override View.
3. Audit and Replay View.
4. Admin and Governance View.

Dependencies:

- UI depends on API contracts and deterministic sample data.

### 7.7 Integration and Testing

1. End-to-end journey 1.
2. End-to-end journey 2.
3. Override recompute and replay.
4. Learning feedback ingestion.

## 8. Agent Setup

### 8.1 Agent Set

The ASE should use the following logical agents:

- Signal Ingestion Agent
- Entity Resolution Agent
- Graph Construction Agent
- Causal Reasoning Agent
- Scenario Simulation Agent
- Strategy Optimization Agent
- Decision Explanation Agent
- Governance and Audit Agent
- Learning Agent

### 8.2 Agent Setup Pattern

For each agent:

1. Environment setup: deploy as a versioned container or module on AKS with managed identity and access to only the stores and APIs it needs.
2. Prompt design: use structured prompts that consume artifact IDs, not raw free-form context.
3. Tool wiring: expose only allowlisted tools such as graph read/write, scenario run, optimization run, ledger append, search, and LLM narration.
4. Memory handling: persist intermediate artifacts in governed stores; do not keep hidden conversational state as the source of truth.
5. Invocation pattern: orchestrator routes a request, agent performs one bounded job, writes outputs, and emits a completion event.

### 8.3 Agent Responsibilities

| Agent | Purpose | Inputs | Outputs | Tools |
|---|---|---|---|---|
| Signal Ingestion Agent | Validate feeds and tag provenance | Raw events, batch files, documents | Canonical signal events, alerts | Event Hubs, ADLS, validation rules |
| Entity Resolution Agent | Resolve identities and survivorship | Canonical entities | Identity links, persistent IDs | Lakehouse, MDM rules, graph updates |
| Graph Construction Agent | Build and update KG | Canonical entities, relationship candidates | Nodes, edges, hypotheses | Graph DB, causal schema |
| Causal Reasoning Agent | Score causal paths and evidence | Graph state, signal events | Evidence classes, driver rankings | KG traversal, causal scoring, search |
| Scenario Simulation Agent | Run what-if scenarios | SDA scope, assumptions, graph context | Scenario runs, sensitivity | Scenario store, feature store, model service |
| Strategy Optimization Agent | Rank alternatives under constraints | Scenario outputs, objective weights, constraints | Pareto frontier, selected option | Optimization engine, policy service |
| Decision Explanation Agent | Render executive narrative | SDA, scorecards, evidence packs | Explanation pack, recommendation card text | Search, LLM orchestration |
| Governance and Audit Agent | Enforce policy and ledgering | SDA, overrides, approvals | Policy check report, ledger entries | Ledger API, audit store, policy engine |
| Learning Agent | Improve confidence and models safely | Outcomes, feedback, drift signals | Promotion request, calibration updates | AML, ledger, telemetry, model registry |

## 9. Infrastructure Mapping

### 9.1 Deployment Model

- Containerized backend services on `AKS`.
- Managed PaaS for data services: `ADLS Gen2`, `Azure SQL`, `Cosmos DB`, `Cosmos DB for Gremlin`, `Azure AI Search`, `Redis`.
- Event and workflow backbone using `Event Hubs` and `Service Bus`.
- AI/ML using `Azure Machine Learning` and `Azure OpenAI`.
- API exposure through `Azure API Management`.

### 9.2 Environment Separation

- Platform subscriptions: `Platform-Management`, `Platform-Connectivity`.
- Workload subscriptions: `CCC-DevTest`, `CCC-Prod`.
- Dev and test can share a non-prod landing zone; production requires separate resource boundaries and private endpoints.

### 9.3 Configuration Management

- Secrets and certificates in `Azure Key Vault`.
- Non-secret operational settings in service configuration or metadata store.
- Policy versions, prompt versions, and model versions must be recorded in the ledger and model registry.

### 9.4 Service to Infrastructure Map

- UI and APIs -> AKS + APIM.
- Ingestion -> Event Hubs, Data Factory, Functions or Logic Apps, ADLS raw.
- Core data -> ADLS curated, Azure SQL, Cosmos DB, Gremlin, AI Search, Redis.
- Learning and model governance -> Azure ML.
- Audit/replay -> immutable object storage plus append-only ledger.

## 10. Technical Stack Mapping

| Component | Stack | Why |
|---|---|---|
| Frontend | Next.js + React + TypeScript | Fast UI composition with enterprise maintainability |
| UI components | Fluent UI | Consistent enterprise patterns |
| Graph visualization | Cytoscape.js or Sigma.js | Suitable for causal and dependency paths |
| Charts | ECharts or Plotly | Good fit for scorecards and scenario comparisons |
| API gateway | Azure API Management | Policy enforcement and routing |
| Identity | Microsoft Entra ID + MSAL | Enterprise SSO and RBAC |
| Runtime | Azure Kubernetes Service | Container orchestration for modular services |
| Images | Azure Container Registry | Controlled container supply chain |
| Ingestion | Azure Event Hubs, Azure Service Bus, Data Factory | Streaming, commands, and batch orchestration |
| Data lake | ADLS Gen2 | Raw and curated landing zones |
| Relational metadata | Azure SQL Database | Operational metadata and structured workflow state |
| Document and scenario data | Azure Cosmos DB | Flexible decision and scenario documents |
| Knowledge graph | Azure Cosmos DB for Apache Gremlin | Property graph support |
| Search | Azure AI Search | Evidence discovery and retrieval |
| Cache | Azure Cache for Redis | Hot lookups and low-latency reads |
| ML governance | Azure Machine Learning | Registry, evaluation, promotion gates |
| LLM | Azure OpenAI | Narration and summary from structured SDA only |
| IaC | Bicep | ALZ-aligned Azure provisioning |
| CI/CD | GitHub Actions or Azure DevOps | Standardized build and deploy flow |

## 11. Risks and Assumptions

### 11.1 POC Shortcuts

- Synthetic or sample data is acceptable for the two journeys.
- Feature engineering and forecasting can be simplified to deterministic or light statistical models.
- Execution adapters can be stubbed if live downstream systems are unavailable.
- Learning can be demonstrated as governed calibration and promotion metadata rather than full production MLOps.

### 11.2 Known Limitations

- Confidence calibration depends on enough outcome history.
- External market signal quality and licensing are outside the PoC boundary.
- Real-time latency is limited by simulation and optimization runtime.
- Graph and scenario fidelity depend on the quality of canonical mappings.

### 11.3 Assumptions

- Systems of record remain external to CCC/ASE.
- All key data objects are tenant-scoped and versioned.
- Audit and replay are mandatory for all recommendation cycles.
- Override is always structured and recompute-driven.

