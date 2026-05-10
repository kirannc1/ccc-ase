# Runbook

## Prerequisites
- Docker Desktop
- Docker Compose v2
- Bash on Linux/macOS
- PowerShell on Windows

## Start System
- Linux/macOS: `./scripts/deploy.sh`
- Windows: `scripts\deploy.cmd`

## Stop System
- Linux/macOS: `./scripts/stop.sh`
- Windows: `docker compose --env-file .env down`

## Reset System
- Linux/macOS: `./scripts/reset.sh`
- Windows: `docker compose --env-file .env down -v --remove-orphans`

## Run Sanity Tests
- Linux/macOS: `./scripts/sanity_test.sh`
- Windows: `scripts\sanity_test.cmd`

## Troubleshooting
- Check `docker compose ps` for unhealthy containers.
- Rebuild after config changes: `docker compose --env-file .env up -d --build`.
- If SQLite files look stale, rerun `./scripts/init_db.sh`.
- If ports conflict, update the service port values in `.env`.
