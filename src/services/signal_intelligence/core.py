from __future__ import annotations

from services.common.models import SignalInsight, SignalIntelligenceResponse
from services.common.storage import SqliteStore


class SignalIntelligenceService:
    def __init__(self, store: SqliteStore) -> None:
        self.store = store

    def score(self, tenant_id: str, top_n: int = 5) -> SignalIntelligenceResponse:
        rows = self.store.fetch_all(
            """
            select feature_name, avg(value) as average_value
            from feature_record
            where tenant_id = ?
            group by feature_name
            order by max(observed_ts) desc
            limit ?
            """,
            (tenant_id, top_n),
        )
        signals = [
            SignalInsight(
                feature_name=row["feature_name"],
                score=round(min(1.0, abs(float(row["average_value"])) / 10.0), 3),
                rationale="feature signal from historical store",
            )
            for row in rows
        ]
        return SignalIntelligenceResponse(tenant_id=tenant_id, signals=signals)

