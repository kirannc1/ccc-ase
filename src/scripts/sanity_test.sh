#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

health() { curl -fsS "$1" >/dev/null; }
post() { curl -fsS -H "Content-Type: application/json" -X POST "$1" -d "$2" >/dev/null; }

health "http://localhost:${SOURCE_CONNECTOR_PORT:-8011}/health"
health "http://localhost:${BATCH_INGESTION_PORT:-8012}/health"
health "http://localhost:${STREAMING_INGESTION_PORT:-8013}/health"
health "http://localhost:${DOCUMENT_PARSING_PORT:-8014}/health"
health "http://localhost:${SEMANTIC_NORMALIZATION_PORT:-8015}/health"
health "http://localhost:${ENTITY_RESOLUTION_PORT:-8016}/health"
health "http://localhost:${FEATURE_ENGINEERING_PORT:-8017}/health"
health "http://localhost:${KNOWLEDGE_GRAPH_PORT:-8018}/health"
health "http://localhost:${KONG_PROXY_PORT:-8000}/health"

post "http://localhost:${SOURCE_CONNECTOR_PORT:-8011}/sources/register" '{"source_id":"hr-core","source_name":"HR Core","source_type":"hrms","config":{"system":"workday"}}'
post "http://localhost:${BATCH_INGESTION_PORT:-8012}/ingest" '{"schema_version":"1.0","tenant_id":"tenant-a","source_system":"workday","source_record_id":"rec-001","payload":{"employee_id":"E-001","name":"Alice"}}'
post "http://localhost:${STREAMING_INGESTION_PORT:-8013}/stream" '{"schema_version":"1.0","tenant_id":"tenant-a","source_system":"workday","source_record_id":"rec-002","payload":{"employee_id":"E-002","name":"Bob"}}'
post "http://localhost:${DOCUMENT_PARSING_PORT:-8014}/parse" '{"schema_version":"1.0","tenant_id":"tenant-a","document_id":"doc-001","document_type":"resume","extracted":{"text":"sample"}}'
post "http://localhost:${SEMANTIC_NORMALIZATION_PORT:-8015}/normalize" '{"schema_version":"1.0","tenant_id":"tenant-a","source_system":"workday","source_record_id":"rec-003","payload":{"employee_id":"E-003","name":"Cara"}}'
post "http://localhost:${ENTITY_RESOLUTION_PORT:-8016}/resolve" '{"schema_version":"1.0","event_id":"evt_001","event_type":"workday.normalized","tenant_id":"tenant-a","domain":"hr","entity_refs":[],"payload":{"employee_id":"E-003"},"provenance":{"source_system":"workday","source_record_id":"rec-003"}}'
post "http://localhost:${FEATURE_ENGINEERING_PORT:-8017}/features/generate" '{"event":{"schema_version":"1.0","event_id":"evt_002","event_type":"workday.normalized","tenant_id":"tenant-a","domain":"hr","entity_refs":[],"payload":{"employee_id":"E-003"},"provenance":{"source_system":"workday","source_record_id":"rec-003"}},"entity":{"schema_version":"1.0","tenant_id":"tenant-a","source_entity_id":"rec-003","entity_id":"ent_001","entity_type":"team","resolution_status":"resolved"}}'
post "http://localhost:${KNOWLEDGE_GRAPH_PORT:-8018}/graph/upsert" '{"entity":{"schema_version":"1.0","tenant_id":"tenant-a","source_entity_id":"rec-003","entity_id":"ent_001","entity_type":"team","resolution_status":"resolved"},"feature":{"schema_version":"1.0","tenant_id":"tenant-a","entity_id":"ent_001","feature_name":"hr_signal_strength","feature_version":"v1","value":1.0,"observed_ts":"2026-05-09T00:00:00Z"}}'
