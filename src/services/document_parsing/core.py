from __future__ import annotations

from services.common.models import ParsedDocument
from services.common.storage import SqliteStore


SCHEMA = """
create table if not exists parsed_document (
  document_id text primary key,
  tenant_id text not null,
  document_type text not null,
  extracted_json text not null
);
create index if not exists idx_parsed_tenant on parsed_document(tenant_id);
"""


class DocumentParsingService:
    def __init__(self, store: SqliteStore) -> None:
        self.store = store
        self.store.executescript(SCHEMA)

    def parse(self, document: ParsedDocument) -> dict[str, str]:
        self.store.execute(
            """
            insert or replace into parsed_document
            (document_id, tenant_id, document_type, extracted_json)
            values (?, ?, ?, ?)
            """,
            (
                document.document_id,
                document.tenant_id,
                document.document_type,
                self.store.json(document.extracted),
            ),
        )
        return {"status": "parsed", "document_id": document.document_id}
