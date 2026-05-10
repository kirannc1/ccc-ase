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

