from __future__ import annotations

from hashlib import sha1

from services.common.models import CanonicalEvent, RawRecord
from services.common.messaging import publish_outbox_event
from services.common.storage import SqliteStore


SCHEMA = """
create table if not exists canonical_event (
  event_id text primary key,
  tenant_id text not null,
  domain text not null,
  event_type text not null,
  payload_json text not null,
  provenance_json text not null,
  created_at text default current_timestamp
);
create index if not exists idx_canonical_tenant on canonical_event(tenant_id);
create index if not exists idx_canonical_domain on canonical_event(domain);
create table if not exists event_outbox (
  outbox_id integer primary key autoincrement,
  event_type text not null,
  payload_json text not null,
  published integer not null default 0,
  created_at text default current_timestamp
);
"""


class SemanticNormalizationService:
    def __init__(self, store: SqliteStore) -> None:
        self.store = store
        self.store.executescript(SCHEMA)

    def normalize(self, record: RawRecord) -> CanonicalEvent:
        domain = self._resolve_domain(record.source_system)
        event_id = sha1(f"{record.tenant_id}:{record.source_system}:{record.source_record_id}".encode()).hexdigest()[:16]
        event = CanonicalEvent(
            event_id=f"evt_{event_id}",
            event_type=f"{record.source_system}.normalized",
            tenant_id=record.tenant_id,
            domain=domain,
            entity_refs=[],
            payload=record.payload,
            provenance={
                "source_system": record.source_system,
                "source_record_id": record.source_record_id,
                "observed_ts": record.observed_ts.isoformat(),
            },
        )
        self.store.execute(
            """
            insert or replace into canonical_event
            (event_id, tenant_id, domain, event_type, payload_json, provenance_json)
            values (?, ?, ?, ?, ?, ?)
            """,
            (
                event.event_id,
                event.tenant_id,
                event.domain,
                event.event_type,
                self.store.json(event.payload),
                self.store.json(event.provenance),
            ),
        )
        publish_outbox_event(self.store, event.event_type, event.model_dump())
        return event

    def _resolve_domain(self, source_system: str) -> str:
        lowered = source_system.lower()
        if lowered in {"workday", "hrms", "hcm"}:
            return "hr"
        if lowered in {"sap", "oracle", "erp", "finance"}:
            return "finance"
        if lowered in {"servicenow", "jira", "ops"}:
            return "operations"
        if lowered in {"cloud", "azure", "aws", "gcp"}:
            return "it"
        return "cross_domain"
