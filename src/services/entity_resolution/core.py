from __future__ import annotations

from hashlib import sha1

from services.common.models import CanonicalEvent, EntityLink
from services.common.storage import SqliteStore


SCHEMA = """
create table if not exists entity_link (
  entity_link_id integer primary key autoincrement,
  tenant_id text not null,
  source_entity_id text not null,
  entity_id text not null,
  entity_type text not null,
  resolution_status text not null,
  created_at text default current_timestamp
);
create index if not exists idx_entity_link_tenant on entity_link(tenant_id);
create index if not exists idx_entity_link_source on entity_link(source_entity_id);
"""


class EntityResolutionService:
    def __init__(self, store: SqliteStore) -> None:
        self.store = store
        self.store.executescript(SCHEMA)

    def resolve(self, event: CanonicalEvent) -> EntityLink:
        source_entity_id = event.provenance["source_record_id"]
        entity_type = self._resolve_entity_type(event.domain)
        entity_id = f"ent_{sha1(f'{event.tenant_id}:{source_entity_id}'.encode()).hexdigest()[:16]}"
        link = EntityLink(
            tenant_id=event.tenant_id,
            source_entity_id=source_entity_id,
            entity_id=entity_id,
            entity_type=entity_type,
        )
        self.store.execute(
            """
            insert or replace into entity_link
            (tenant_id, source_entity_id, entity_id, entity_type, resolution_status)
            values (?, ?, ?, ?, ?)
            """,
            (link.tenant_id, link.source_entity_id, link.entity_id, link.entity_type, link.resolution_status),
        )
        return link

    def _resolve_entity_type(self, domain: str) -> str:
        if domain == "hr":
            return "team"
        if domain == "finance":
            return "cost_center"
        if domain == "operations":
            return "service"
        if domain == "it":
            return "platform"
        return "other"
