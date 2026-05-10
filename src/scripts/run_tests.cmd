@echo off
setlocal
cd /d "%~dp0\.."

call scripts\sanity_test.cmd || exit /b 1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\setup_agents.ps1 >nul
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$agents = @('signal_ingestion','entity_resolution','graph_construction','causal_reasoning','scenario_simulation','strategy_optimization','decision_explanation','governance_audit','learning');" ^
  "$agents | ForEach-Object { if (-not (Test-Path (Join-Path ('agents/' + $_) 'agent.md'))) { throw $_ }; if (-not (Test-Path (Join-Path ('agents/' + $_) 'prompt.txt'))) { throw $_ } };" ^
  "Write-Host 'agents ok'"

echo tests ok
