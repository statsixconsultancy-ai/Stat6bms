# BMS Microservices Start Script (PowerShell)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = Split-Path -Parent $ScriptDir
$PythonExe = Join-Path $BackendDir "venv\Scripts\python.exe"

if (-not (Test-Path $PythonExe)) {
    $PythonExe = "python"
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  Launching BMS Distributed Microservices via Python Orchestrator" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan

$env:PYTHONPATH = $BackendDir
& $PythonExe (Join-Path $ScriptDir "dev_orchestrator.py")
