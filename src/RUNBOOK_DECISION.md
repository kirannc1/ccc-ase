# Decision Runbook

## Start Services
- `docker compose --env-file .env up -d --build scenario_simulation optimization decisioning decision_explanation`

## Flow
- Scenario: `POST /scenario/simulate`
- Optimization: `POST /optimization/rank`
- Decisioning: `POST /decision/resolve`
- Explanation: `POST /explanation/generate`

## Run Tests
- `docker compose --env-file .env run --rm --build scenario_simulation python -m pytest -q services/scenario_simulation/tests services/optimization/tests services/decisioning/tests services/decision_explanation/tests`

## Troubleshooting
- Rebuild if imports change: `docker compose --env-file .env up -d --build`
- Check `docker compose ps` for unhealthy decision services
- Verify upstream services: `feature_engineering`, `knowledge_graph`, `policy_service`
