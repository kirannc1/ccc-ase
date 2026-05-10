#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

[ -f .env ] || cp .env.template .env
docker compose --env-file .env up -d --build

for url in \
  "http://localhost:${SOURCE_CONNECTOR_PORT:-8011}/health" \
  "http://localhost:${BATCH_INGESTION_PORT:-8012}/health" \
  "http://localhost:${STREAMING_INGESTION_PORT:-8013}/health" \
  "http://localhost:${DOCUMENT_PARSING_PORT:-8014}/health" \
  "http://localhost:${SEMANTIC_NORMALIZATION_PORT:-8015}/health" \
  "http://localhost:${ENTITY_RESOLUTION_PORT:-8016}/health" \
  "http://localhost:${FEATURE_ENGINEERING_PORT:-8017}/health" \
  "http://localhost:${KNOWLEDGE_GRAPH_PORT:-8018}/health" \
  "http://localhost:${KONG_PROXY_PORT:-8000}/health"
do
  ready=0
  for _ in 1 2 3 4 5 6 7 8 9 10 11 12; do
    if curl -fsS "$url" >/dev/null; then
      ready=1
      break
    fi
    sleep 5
  done
  [ "$ready" -eq 1 ]
done

./scripts/init_db.sh
./scripts/sanity_test.sh
