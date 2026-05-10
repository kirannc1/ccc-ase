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

