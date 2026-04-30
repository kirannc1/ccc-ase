# `ase-orchestrator`

ASE control-plane service responsible for:

- event-driven workflow routing across agents
- correlation IDs + idempotency keys
- recompute orchestration for overrides
- emitting immutable ledger entries via `ledger-api`

