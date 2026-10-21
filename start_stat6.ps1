# ==============================================================================
# STAT6 Enterprise Business Management System - 1-Click Production Launcher
# Starts the Unified 14-Module FastAPI Gateway (:8000) & React/Vite UI (:3000)
# ==============================================================================
$ErrorActionPreference = "Continue"
$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = Join-Path $RootDir "backend"
$FrontendDir = Join-Path $RootDir "frontend"

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "  STAT6 BMS Enterprise Production Release Launcher (v2.4)" -ForegroundColor Cyan
Write-Host "  14 Canonical Modules, 4D-RBAC, PBKDF2 Vault, AI Copilot" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan

$PythonExe = Join-Path $BackendDir "venv\Scripts\python.exe"
if (-Not (Test-Path $PythonExe)) {
    $PythonExe = "python"
}

Write-Host "[1/2] Starting STAT6 Unified API Gateway on http://127.0.0.1:8000 ..." -ForegroundColor Green
Start-Process -FilePath $PythonExe -ArgumentList "-m", "uvicorn", "services.gateway.main:app", "--host", "0.0.0.0", "--port", "8000" -WorkingDirectory $BackendDir

Write-Host "[2/2] Starting STAT6 Unified React/Vite UI on http://localhost:3000 ..." -ForegroundColor Green
Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "npm run dev -- --host 0.0.0.0" -WorkingDirectory $FrontendDir

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "STAT6 is now running!" -ForegroundColor Yellow
Write-Host " -> Backend API Gateway and OpenAPI Docs : http://127.0.0.1:8000/docs"
Write-Host " -> Frontend Enterprise Console         : http://localhost:3000"
Write-Host " -> Master Superadmin Login             : admin@acroflow.enterprise / Password123!"
