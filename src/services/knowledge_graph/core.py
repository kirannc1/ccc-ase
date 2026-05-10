from __future__ import annotations

from services.common.models import EntityLink, FeatureRecord, GraphRelation, GraphWriteRequest
from services.common.messaging import publish_outbox_event
from services.common.storage import SqliteStore


SCHEMA = """
create table if not exists graph_node (
  node_id text primary key,
  tenant_id text not null,
  node_type text not null,
  source_entity_id text not null,
  created_at text default current_timestamp
);
create table if not exists graph_relation (
  relation_id integer primary key autoincrement,
  tenant_id text not null,
  from_node_id text not null,
  to_node_id text not null,
  relation_type text not null,
  evidence_class text not null,
  confidence real not null
);
create index if not exists idx_graph_node_tenant on graph_node(tenant_id);
create index if not exists idx_graph_rel_tenant on graph_relation(tenant_id);
create table if not exists event_outbox (
  outbox_id integer primary key autoincrement,
  event_type text not null,
  payload_json text not null,
  published integer not null default 0,
  created_at text default current_timestamp
);
"""


class KnowledgeGraphService:
    def __init__(self, store: SqliteStore) -> None:
        self.store = store
        self.store.executescript(SCHEMA)

    def upsert(self, request: GraphWriteRequest) -> GraphRelation:
        from_node_id = request.entity.entity_id
        to_node_id = request.feature.entity_id if request.feature else request.entity.entity_id
        relation = GraphRelation(
            tenant_id=request.entity.tenant_id,
            from_entity_id=from_node_id,
            to_entity_id=to_node_id,
            relation_type="observes",
            evidence_class="statistically_supported_link",
            confidence=0.7 if request.feature else 0.5,
        )
        self.store.execute(
            """
            insert or replace into graph_node (node_id, tenant_id, node_type, source_entity_id)
            values (?, ?, ?, ?)
            """,
            (request.entity.entity_id, request.entity.tenant_id, request.entity.entity_type, request.entity.source_entity_id),
        )
        if request.feature:
            self.store.execute(
                """
                insert or replace into graph_node (node_id, tenant_id, node_type, source_entity_id)
                values (?, ?, ?, ?)
                """,
                (request.feature.entity_id, request.feature.tenant_id, "feature", request.feature.entity_id),
            )
        self.store.execute(
            """
            insert into graph_relation
            (tenant_id, from_node_id, to_node_id, relation_type, evidence_class, confidence)
            values (?, ?, ?, ?, ?, ?)
            """,
            (
                relation.tenant_id,
                relation.from_entity_id,
                relation.to_entity_id,
                relation.relation_type,
                relation.evidence_class,
                relation.confidence,
            ),
        )
        publish_outbox_event(self.store, "graph.updated", relation.model_dump())
        return relation
