create table if not exists raw_ingestion (
  ingestion_id integer primary key autoincrement,
  tenant_id text not null,
  source_system text not null,
  source_record_id text not null,
  payload_json text not null,
  observed_ts text not null,
  unique (tenant_id, source_system, source_record_id)
);
create index if not exists idx_raw_ingestion_tenant on raw_ingestion(tenant_id);

