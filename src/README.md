# `src/` Code Structure (CCC / ASE)

This folder is a recommended mono-repo layout for implementing the CCC/ASE design in this workspace.

## High-level layout

```
src/
  apps/
    leadership-web/          # Next.js UI for leadership decisioning
    ops-console/             # Next.js UI for strategy ops / analysts
    governance-console/      # Next.js UI for governance, audit, replay

  services/
    ase-orchestrator/        # ASE control plane (workflow routing, correlation, idempotency)
    tool-guardrails/         # Tool registry + constraints + redaction + approval gates
    ledger-api/              # Append-only ledger write + replay read APIs

    agents/                  # Agent-aligned services (logical roles)
      ingestion/
      entity-resolution/
      graph-construction/
      causal-reasoning/
      scenario-simulation/
      strategy-optimization/
      decision-explanation/
      governance-audit/
      learning/

    core/                    # Capability services used by agents
      normalization/
      signal-intelligence/
      knowledge-graph/
      scenario/
      optimization/
      decisioning/
      explanation/
      policy-constraints/

  shared/
    contracts/               # Frozen schemas (SDA, scenario, override, audit) + OpenAPI/JSON schema
    observability/           # Logging/metrics/tracing helpers
    auth/                    # Entra/MSAL helpers, token validation, RBAC/ABAC policy hooks
    storage/                 # Store clients (lakehouse, graph, scenario store, ledger artifacts)
```

## Implementation rules (recommended)

- Treat `api_contracts.md` as the source-of-truth for payload schemas; generate JSON Schema / OpenAPI into `src/shared/contracts/`.
- Keep `decision_standards.md` enforced at service boundaries (SDA-first, append-only ledger, controlled overrides).
- Agents should write artifacts and references, not pass opaque text blobs between services.

