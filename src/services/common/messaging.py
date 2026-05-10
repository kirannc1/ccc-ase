from __future__ import annotations

from services.common.storage import SqliteStore


def publish_outbox_event(store: SqliteStore, event_type: str, payload: dict) -> None:
    store.execute(
        "insert into event_outbox (event_type, payload_json) values (?, ?)",
        (event_type, store.json(payload)),
    )

