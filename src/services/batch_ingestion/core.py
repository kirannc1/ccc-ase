from __future__ import annotations

from services.common.models import RawRecord
from services.common.storage import SqliteStore


SCHEMA = """
create table if not exists raw_batch_ingestion (
  ingestion_id integer primary key autoincrement,
  tenant_id text not null,
  source_system text not null,
  source_record_id text not null,
  payload_json text not null,
  observed_ts text not null
);
create index if not exists idx_raw_batch_tenant on raw_batch_ingestion(tenant_id);
create index if not exists idx_raw_batch_source on raw_batch_ingestion(source_system, source_record_id);
"""


class BatchIngestionService:
    def __init__(self, store: SqliteStore) -> None:
        self.store = store
        self.store.executescript(SCHEMA)

    def ingest(self, record: RawRecord) -> dict[str, str]:
        self.store.execute(
            """
            insert into raw_batch_ingestion
            (tenant_id, source_system, source_record_id, payload_json, observed_ts)
            values (?, ?, ?, ?, ?)
            """,
            (
                record.tenant_id,
                record.source_system,
                record.source_record_id,
                self.store.json(record.payload),
                record.observed_ts.isoformat(),
            ),
        )
        return {"status": "ingested", "source_record_id": record.source_record_id}
