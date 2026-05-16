$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)

if (-not (Test-Path .env)) { Copy-Item .env.template .env }

if (-not (Test-Path .dockerignore)) {
@'
.git
.github
.vscode
**/__pycache__/
**/*.pyc
.tmp-test
.tmp-support
.dbcheck
.sqlite
*.db
*.db-journal
*.sqlite
*.sqlite-journal
ui/node_modules
ui/.next
ui/out
ui/dist
*.log
'@ | Set-Content -Encoding UTF8 -NoNewline .dockerignore
}

$env:DOCKER_BUILDKIT = '1'
$env:COMPOSE_DOCKER_CLI_BUILD = '1'

$args = @('--env-file', '.env', 'up', '-d', '--build')
if ($env:FORCE_REBUILD -eq '1') { $args += @('--no-cache') }
docker compose @args

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

function Wait-Health([string]$Url) {
  for ($i = 0; $i -lt 60; $i++) {
    try { Invoke-RestMethod -Method Get -Uri $Url | Out-Null; return } catch { Start-Sleep -Seconds 5 }
  }
  throw "timeout $Url"
}

Wait-Health "http://localhost:$($ports.source)/health"
Wait-Health "http://localhost:$($ports.batch)/health"
Wait-Health "http://localhost:$($ports.stream)/health"
Wait-Health "http://localhost:$($ports.parse)/health"
Wait-Health "http://localhost:$($ports.normalize)/health"
Wait-Health "http://localhost:$($ports.entity)/health"
Wait-Health "http://localhost:$($ports.feature)/health"
Wait-Health "http://localhost:$($ports.graph)/health"
Wait-Health "http://localhost:$($ports.kong)/health"

docker compose --env-file .env exec -T source_connector python /app/scripts/init_db.py
& "$PSScriptRoot/sanity_test.ps1"
