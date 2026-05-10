from __future__ import annotations

from services.common.models import SourceRegistration
from services.common.storage import SqliteStore


SCHEMA = """
create table if not exists source_registration (
  source_id text primary key,
  source_name text not null,
  source_type text not null,
  config_json text not null,
  created_at text default current_timestamp
);
"""


class SourceConnectorService:
    def __init__(self, store: SqliteStore) -> None:
        self.store = store
        self.store.executescript(SCHEMA)

    def register(self, registration: SourceRegistration) -> dict[str, str]:
        self.store.execute(
            """
            insert or replace into source_registration
            (source_id, source_name, source_type, config_json)
            values (?, ?, ?, ?)
            """,
            (
                registration.source_id,
                registration.source_name,
                registration.source_type,
                self.store.json(registration.config),
            ),
        )
        return {"source_id": registration.source_id, "status": "registered"}
