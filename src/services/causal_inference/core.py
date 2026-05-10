from __future__ import annotations

from services.common.models import CausalRequest, CausalResponse
from services.common.storage import SqliteStore


class CausalInferenceService:
    def __init__(self, store: SqliteStore) -> None:
        self.store = store

    def infer(self, request: CausalRequest) -> CausalResponse:
        relation = self.store.fetch_one(
            """
            select relation_type, confidence
            from graph_relation
            where tenant_id = ? and from_node_id = ? and to_node_id = ?
            order by relation_id desc
            limit 1
            """,
            (request.tenant_id, request.source_entity_id, request.target_entity_id),
        )
        if relation:
            return CausalResponse(
                tenant_id=request.tenant_id,
                source_entity_id=request.source_entity_id,
                target_entity_id=request.target_entity_id,
                relation_type=relation["relation_type"],
                confidence=float(relation["confidence"]),
                explanation="existing graph relation",
            )
        return CausalResponse(
            tenant_id=request.tenant_id,
            source_entity_id=request.source_entity_id,
            target_entity_id=request.target_entity_id,
            relation_type=None,
            confidence=0.4,
            explanation="heuristic similarity fallback",
        )

