$ErrorActionPreference = 'Stop'

function Test-Health([string]$Url) {
  Invoke-RestMethod -Method Get -Uri $Url | Out-Null
}

function Test-Post([string]$Url, [string]$Body) {
  Invoke-RestMethod -Method Post -Uri $Url -ContentType 'application/json' -Body $Body | Out-Null
}

$ports = @{
  source    = if ($env:SOURCE_CONNECTOR_PORT) { [int]$env:SOURCE_CONNECTOR_PORT } else { 8011 }
  batch     = if ($env:BATCH_INGESTION_PORT) { [int]$env:BATCH_INGESTION_PORT } else { 8012 }
  stream    = if ($env:STREAMING_INGESTION_PORT) { [int]$env:STREAMING_INGESTION_PORT } else { 8013 }
  parse     = if ($env:DOCUMENT_PARSING_PORT) { [int]$env:DOCUMENT_PARSING_PORT } else { 8014 }
  normalize = if ($env:SEMANTIC_NORMALIZATION_PORT) { [int]$env:SEMANTIC_NORMALIZATION_PORT } else { 8015 }
  entity    = if ($env:ENTITY_RESOLUTION_PORT) { [int]$env:ENTITY_RESOLUTION_PORT } else { 8016 }
  feature   = if ($env:FEATURE_ENGINEERING_PORT) { [int]$env:FEATURE_ENGINEERING_PORT } else { 8017 }
  graph     = if ($env:KNOWLEDGE_GRAPH_PORT) { [int]$env:KNOWLEDGE_GRAPH_PORT } else { 8018 }
  kong      = if ($env:KONG_PROXY_PORT) { [int]$env:KONG_PROXY_PORT } else { 8000 }
}

Test-Health "http://localhost:$($ports.source)/health"
Test-Health "http://localhost:$($ports.batch)/health"
Test-Health "http://localhost:$($ports.stream)/health"
Test-Health "http://localhost:$($ports.parse)/health"
Test-Health "http://localhost:$($ports.normalize)/health"
Test-Health "http://localhost:$($ports.entity)/health"
Test-Health "http://localhost:$($ports.feature)/health"
Test-Health "http://localhost:$($ports.graph)/health"
Test-Health "http://localhost:$($ports.kong)/health"

Test-Post "http://localhost:$($ports.source)/sources/register" '{"source_id":"hr-core","source_name":"HR Core","source_type":"hrms","config":{"system":"workday"}}'
Test-Post "http://localhost:$($ports.batch)/ingest" '{"schema_version":"1.0","tenant_id":"tenant-a","source_system":"workday","source_record_id":"rec-001","payload":{"employee_id":"E-001","name":"Alice"}}'
Test-Post "http://localhost:$($ports.stream)/stream" '{"schema_version":"1.0","tenant_id":"tenant-a","source_system":"workday","source_record_id":"rec-002","payload":{"employee_id":"E-002","name":"Bob"}}'
Test-Post "http://localhost:$($ports.parse)/parse" '{"schema_version":"1.0","tenant_id":"tenant-a","document_id":"doc-001","document_type":"resume","extracted":{"text":"sample"}}'
Test-Post "http://localhost:$($ports.normalize)/normalize" '{"schema_version":"1.0","tenant_id":"tenant-a","source_system":"workday","source_record_id":"rec-003","payload":{"employee_id":"E-003","name":"Cara"}}'
Test-Post "http://localhost:$($ports.entity)/resolve" '{"schema_version":"1.0","event_id":"evt_001","event_type":"workday.normalized","tenant_id":"tenant-a","domain":"hr","entity_refs":[],"payload":{"employee_id":"E-003"},"provenance":{"source_system":"workday","source_record_id":"rec-003"}}'
Test-Post "http://localhost:$($ports.feature)/features/generate" '{"event":{"schema_version":"1.0","event_id":"evt_002","event_type":"workday.normalized","tenant_id":"tenant-a","domain":"hr","entity_refs":[],"payload":{"employee_id":"E-003"},"provenance":{"source_system":"workday","source_record_id":"rec-003"}},"entity":{"schema_version":"1.0","tenant_id":"tenant-a","source_entity_id":"rec-003","entity_id":"ent_001","entity_type":"team","resolution_status":"resolved"}}'
Test-Post "http://localhost:$($ports.graph)/graph/upsert" '{"entity":{"schema_version":"1.0","tenant_id":"tenant-a","source_entity_id":"rec-003","entity_id":"ent_001","entity_type":"team","resolution_status":"resolved"},"feature":{"schema_version":"1.0","tenant_id":"tenant-a","entity_id":"ent_001","feature_name":"hr_signal_strength","feature_version":"v1","value":1.0,"observed_ts":"2026-05-09T00:00:00Z"}}'
