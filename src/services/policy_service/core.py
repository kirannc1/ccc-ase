from __future__ import annotations

from services.common.models import PolicyRequest, PolicyResponse
from services.common.storage import SqliteStore


class PolicyService:
    def __init__(self, store: SqliteStore) -> None:
        self.store = store

    def evaluate(self, request: PolicyRequest) -> PolicyResponse:
        metrics = dict(request.metrics)
        if not metrics:
            rows = self.store.fetch_all(
                """
                select feature_name, value
                from feature_record
                where tenant_id = ?
                order by observed_ts desc
                """,
                (request.tenant_id,),
            )
            for row in rows:
                metrics.setdefault(row["feature_name"], float(row["value"]))
        violations: list[str] = []
        for name, limit_value in request.constraints.items():
            metric_value = metrics.get(name)
            if metric_value is None:
                continue
            if metric_value > limit_value:
                violations.append(f"{name}>{limit_value}")
        return PolicyResponse(
            tenant_id=request.tenant_id,
            allowed=not violations,
            violations=violations,
            evaluated_metrics=metrics,
        )

