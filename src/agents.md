# Agents

## A. Agent Setup Pattern
- `env setup`: one shared runtime, shared contracts, shared artifact paths
- `prompt pattern`: artifact-driven prompts that reference `poc_LLD.md`, `api_contracts.md`, `data_architecture.md`
- `tool wiring`: allowlist only; read contracts, write designated service outputs, no ad-hoc tooling
- `memory`: externalized in per-agent `memory.json` or shared store; keep prompts stateless
- `invocation`: orchestrated from a single registry, one agent at a time or staged in a pipeline

## B. Agent Template
- `name`: `<agent_name>`
- `inputs`: artifact refs, current state, task slice
- `outputs`: plan, generated artifact, validation notes
- `tools`: read-only docs, scoped file write, optional shell
- `execution steps`: load context; inspect artifacts; produce scoped output; persist result; emit status

## C. Agent Registry
| Name | Purpose | Inputs | Outputs | Tools |
|---|---|---|---|---|
| `signal_ingestion` | Capture and shape source signals | source docs, contracts | signal payloads | docs, file write |
| `entity_resolution` | Link sources to canonical entities | normalized events | entity links | docs, file write |
| `graph_construction` | Build graph relations | entity links, features | graph writes | docs, file write |
| `causal_reasoning` | Infer causal paths | graph data, rules | causal traces | docs, file write |
| `scenario_simulation` | Simulate alternatives | causal traces, scenarios | scenario outputs | docs, file write |
| `strategy_optimization` | Rank recommendations | scenarios, weights | ranked actions | docs, file write |
| `decision_explanation` | Explain recommendation outcomes | scores, traces | explanation payloads | docs, file write |
| `governance_audit` | Capture overrides and audit trail | decisions, overrides | audit records | docs, file write |
| `learning` | Promote feedback into memory | outcomes, feedback | learning updates | docs, file write |
