from __future__ import annotations

from services.common.models import FeatureGenerationRequest, FeatureRecord
from services.common.messaging import publish_outbox_event
from services.common.storage import SqliteStore


SCHEMA = """
create table if not exists feature_record (
  feature_id integer primary key autoincrement,
  tenant_id text not null,
  entity_id text not null,
  feature_name text not null,
  feature_version text not null,
  value real not null,
  observed_ts text not null
);
create index if not exists idx_feature_tenant on feature_record(tenant_id);
create index if not exists idx_feature_entity on feature_record(entity_id);
create table if not exists event_outbox (
  outbox_id integer primary key autoincrement,
  event_type text not null,
  payload_json text not null,
  published integer not null default 0,
  created_at text default current_timestamp
);
"""


class FeatureEngineeringService:
    def __init__(self, store: SqliteStore) -> None:
        self.store = store
        self.store.executescript(SCHEMA)

    def generate(self, request: FeatureGenerationRequest) -> FeatureRecord:
        value = float(len(request.event.payload)) / 10.0
        feature = FeatureRecord(
            tenant_id=request.entity.tenant_id,
            entity_id=request.entity.entity_id,
            feature_name=f"{request.event.domain}_signal_strength",
            value=value,
        )
        self.store.execute(
            """
            insert into feature_record
            (tenant_id, entity_id, feature_name, feature_version, value, observed_ts)
            values (?, ?, ?, ?, ?, ?)
            """,
            (
                feature.tenant_id,
                feature.entity_id,
                feature.feature_name,
                feature.feature_version,
                feature.value,
                feature.observed_ts.isoformat(),
            ),
        )
        publish_outbox_event(self.store, "feature.generated", feature.model_dump())
        return feature
