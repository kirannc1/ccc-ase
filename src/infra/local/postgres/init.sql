create table if not exists service_registry (
  service_id text primary key,
  service_name text not null,
  version text not null,
  created_at timestamptz default now()
);

