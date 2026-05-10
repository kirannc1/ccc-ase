$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)

$agents = @(
  'signal_ingestion',
  'entity_resolution',
  'graph_construction',
  'causal_reasoning',
  'scenario_simulation',
  'strategy_optimization',
  'decision_explanation',
  'governance_audit',
  'learning'
)

New-Item -ItemType Directory -Force -Path 'agents' | Out-Null
$registry = @()

foreach ($agent in $agents) {
  $dir = Join-Path 'agents' $agent
  New-Item -ItemType Directory -Force -Path $dir | Out-Null
  $config = @{ name = $agent; enabled = $true; version = '1.0' } | ConvertTo-Json -Compress
  Set-Content -Path (Join-Path $dir 'config.json') -Value $config -Encoding UTF8
  Set-Content -Path (Join-Path $dir 'prompt.txt') -Value "Use the shared agent template for $agent." -Encoding UTF8
  $registry += [ordered]@{ name = $agent; path = "agents/$agent" }
}

$registry | ConvertTo-Json -Depth 3 | Set-Content -Path 'agents/registry.json' -Encoding UTF8
Write-Host 'agents initialized'
