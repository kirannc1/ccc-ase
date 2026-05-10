create table if not exists canonical_event (
  event_id text primary key,
  tenant_id text not null,
  domain text not null,
  event_type text not null,
  payload_json text not null,
  provenance_json text not null,
  created_at text default current_timestamp
);
create index if not exists idx_canonical_event_tenant on canonical_event(tenant_id);
create index if not exists idx_canonical_event_domain on canonical_event(domain);

