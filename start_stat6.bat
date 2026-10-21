@echo off
title STAT6 BMS — 1-Click Production Release Launcher
echo ==================================================================
echo   STAT6 BMS — Enterprise Production Release Launcher (v2.4)
echo   14 Canonical Modules ^| 4D-RBAC ^| PBKDF2 Vault ^| AI Copilot
echo ==================================================================
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_stat6.ps1"
pause
