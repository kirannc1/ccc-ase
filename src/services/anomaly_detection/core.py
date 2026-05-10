from __future__ import annotations

from statistics import pstdev

from services.common.models import AnomalyRequest, AnomalyResponse
from services.common.storage import SqliteStore


class AnomalyDetectionService:
    def __init__(self, store: SqliteStore) -> None:
        self.store = store

    def detect(self, request: AnomalyRequest) -> AnomalyResponse:
        rows = self.store.fetch_all(
            """
            select value
            from feature_record
            where tenant_id = ? and feature_name = ?
            order by observed_ts asc
            """,
            (request.tenant_id, request.feature_name),
        )
        history = [float(row["value"]) for row in rows]
        mean_value = sum(history) / len(history) if history else 0.0
        stddev = pstdev(history) if len(history) > 1 else 0.0
        z_score = 0.0 if stddev == 0 else (request.value - mean_value) / stddev
        anomaly = abs(z_score) > request.threshold
        return AnomalyResponse(
            tenant_id=request.tenant_id,
            feature_name=request.feature_name,
            value=request.value,
            mean=round(mean_value, 3),
            stddev=round(stddev, 3),
            z_score=round(z_score, 3),
            anomaly=anomaly,
        )

