#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

docker compose --env-file .env exec -T source_connector python /app/scripts/init_db.py
