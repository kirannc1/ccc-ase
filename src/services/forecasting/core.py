from __future__ import annotations

from statistics import mean

from services.common.models import ForecastRequest, ForecastResponse
from services.common.storage import SqliteStore


class ForecastingService:
    def __init__(self, store: SqliteStore) -> None:
        self.store = store

    def forecast(self, request: ForecastRequest) -> ForecastResponse:
        rows = self.store.fetch_all(
            """
            select value
            from feature_record
            where tenant_id = ? and entity_id = ? and feature_name = ?
            order by observed_ts asc
            """,
            (request.tenant_id, request.entity_id, request.feature_name),
        )
        history = [float(row["value"]) for row in rows]
        if not history:
            return ForecastResponse(
                tenant_id=request.tenant_id,
                entity_id=request.entity_id,
                feature_name=request.feature_name,
                forecast=0.0,
                trend=0.0,
                history=[],
            )
        if len(history) == 1:
            forecast = history[-1]
            trend = 0.0
        else:
            trend = (history[-1] - history[0]) / (len(history) - 1)
            forecast = history[-1] + trend * request.horizon
        return ForecastResponse(
            tenant_id=request.tenant_id,
            entity_id=request.entity_id,
            feature_name=request.feature_name,
            forecast=round(float(forecast), 3),
            trend=round(float(trend), 3),
            history=history,
        )

