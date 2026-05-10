create table if not exists graph_node (
  node_id text primary key,
  tenant_id text not null,
  node_type text not null,
  source_entity_id text not null,
  created_at text default current_timestamp
);
create table if not exists graph_relation (
  relation_id integer primary key autoincrement,
  tenant_id text not null,
  from_node_id text not null,
  to_node_id text not null,
  relation_type text not null,
  evidence_class text not null,
  confidence real not null
);
create index if not exists idx_graph_node_tenant on graph_node(tenant_id);
create index if not exists idx_graph_rel_tenant on graph_relation(tenant_id);

