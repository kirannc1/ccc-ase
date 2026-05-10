create table if not exists approval_ledger (
  approval_id text primary key,
  tenant_id text not null,
  recommendation_id text not null,
  requested_by text not null,
  status text not null,
  current_stage_index integer not null default 0,
  stages_json text not null,
  history_json text not null,
  metadata_json text not null,
  decided_by text,
  decided_reason text,
  created_at text not null,
  updated_at text not null
);

create table if not exists override_ledger (
  override_id text primary key,
  tenant_id text not null,
  recommendation_id text not null,
  decision_id text not null unique,
  actor_id text not null,
  reason text not null,
  override_status text not null,
  created_at text not null
);

create table if not exists execution_ledger (
  action_id text primary key,
  tenant_id text not null,
  recommendation_id text not null,
  adapter_name text not null,
  status text not null,
  attempts integer not null,
  details_json text not null,
  correlation_id text,
  created_at text not null
);

create table if not exists audit_event_ledger (
  event_id text primary key,
  tenant_id text not null,
  correlation_id text not null,
  event_type text not null,
  resource_id text not null,
  payload_json text not null,
  created_at text not null
);

create table if not exists model_registry_ledger (
  model_id text not null,
  version text not null,
  name text not null,
  status text not null,
  config_json text not null,
  created_at text not null,
  updated_at text not null,
  primary key (model_id, version)
);

create table if not exists learning_dataset_ledger (
  learning_id text primary key,
  tenant_id text not null,
  recommendation_id text not null,
  decision_id text not null,
  signal real not null,
  notes_json text not null,
  created_at text not null
);
