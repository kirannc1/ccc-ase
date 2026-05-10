# PoC Scope: CCC / ASE (Hackathon-Ready)

This PoC scope defines the minimum end-to-end capability of the Cognitive Command Center (CCC) / Autonomous Strategy Engine (ASE) to demonstrate strategic decisioning with:

- multi-domain signal ingestion
- causal graph reasoning
- what-if simulation + multi-objective optimization
- explainable recommendations (SDA-based)
- human override with recomputation and audit/replay

Primary validation references:

- `decision_standards.md`
- `solution_validation_checklist.md`
- `api_contracts.md`

## 1. PoC Goals (What Success Looks Like)

- Demonstrate two executive decision journeys end-to-end with credible artifacts, not slides.
- Show structured recommendation outputs derived from an SDA (no “LLM-only” decisioning).
- Prove trust controls: causal evidence classification, confidence breakdown, scorecards, and immutable audit trace.
- Prove recomputation: override changes assumptions/weights and triggers scenario + optimization recompute with before/after deltas.

## 2. In-Scope Journeys (PoC Must Deliver)

### Journey 1: Attrition Spike in a Critical Delivery Team

**Signals (inputs):**

- engagement drop
- absenteeism spike
- delayed backfills / time-to-fill increase
- market offer acceptance increase (external signal)

**Graph (reasoning):**

- causal path: signals → `skill fragility` → `SLA breach probability` → `revenue/penalty exposure`
- evidence class and confidence visible on the key path(s)

**Scenarios (simulation):**

- `no_action`
- `targeted_retention`
- `redeploy_internal`
- `selective_hiring`
- `automation_investment`

**Outputs (decision):**

- recommendation with:
  - confidence breakdown (components + overall band)
  - top drivers (ranked)
  - standardized scorecards
  - at least 2 alternatives with trade-offs

### Journey 2: Cost Pressure with Demand Uncertainty

**Signals (inputs):**

- cloud cost drift
- vendor rate inflation
- forecast uncertainty (demand confidence reduction)

**Scenarios (simulation):**

- `blanket_cuts`
- `selective_deferral`
- `automation`
- `workload_rebalancing`

**Outputs (decision):**

- trade-off view:
  - objective deltas under the selected weight set
  - at least 2 near-optimal alternatives with deltas

## 3. Override Demo (PoC Must Deliver)

Override MUST be demonstrated on at least one journey:

- Change assumptions and/or objective weights (e.g., enforce hiring freeze, tighten budget cap, increase resilience weight).
- Trigger recomputation of scenarios, optimization, and confidence.
- Show before/after deltas for:
  - recommendation (selected option + alternatives)
  - scorecards
  - confidence (components + band)
- Show immutable audit trace:
  - original decision preserved
  - override recorded with controlled `override_type` and `reason_code`
  - recompute artifacts linked in the Decision Ledger

## 4. Minimum Data Required (Synthetic Allowed)

To run this PoC with synthetic/sample data:

- HR: engagement score time series, absenteeism time series, hiring pipeline/backfill delay metrics, attrition risk indicator
- Ops: SLA metrics, throughput/cycle time indicators for impacted team/service
- Finance: cost center / revenue exposure proxies, penalty exposure proxy
- IT/Cloud: cloud cost time series by service/team
- External: offer acceptance / labor market proxy + vendor inflation index

All signals must carry provenance (source, timestamp, freshness) and map to canonical entities (team/service/cost center).

## 5. Locked Decision Outputs (Standards Compliance)

PoC MUST comply with these locked standards:

- SDA is the source of truth (DS-001, DS-010..DS-027).
- Causal evidence class is explicit; counterevidence is not suppressed (DS-002, DS-030..DS-033, DS-122).
- Confidence components + overall band are present and drive governance behavior (DS-060..DS-066).
- Scorecards use locked schema and scoring ranges (DS-110..DS-113).
- Overrides use controlled types and reason codes (DS-073..DS-075).

## 6. Out of Scope (Explicit)

- Source-system replacement (ERP/HCM/ITSM remain systems of record).
- Fully autonomous execution without approvals.
- Full enterprise-grade data governance program (PoC demonstrates hooks, not complete policy rollout).
- Full MLOps maturity (PoC demonstrates governed learning signals and versioning concepts).

## 7. PoC Acceptance Criteria (Go/No-Go)

- Both journeys produce an explainable recommendation with:
  - causal path evidence classification
  - confidence breakdown + band
  - standardized scorecards
  - alternatives and trade-offs
- Override recomputation demonstrated with before/after deltas and ledger-tracked traceability.
- Replay demonstrated for at least one completed recommendation cycle.

