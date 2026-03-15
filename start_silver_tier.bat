@echo off
echo ============================================
echo AI Employee - Silver Tier Startup
echo ============================================
echo.

echo [1/3] Starting Gmail Watcher...
start "Gmail Watcher" python watchers\gmail_watcher.py AI_Employee_Vault
timeout /t 2 /nobreak >nul

echo [2/3] Starting Gmail Smart Responder...
start "Gmail Smart Responder" python watchers\gmail_smart_responder.py AI_Employee_Vault
timeout /t 2 /nobreak >nul

echo [3/3] Starting Orchestrator...
start "Orchestrator" python orchestrator.py AI_Employee_Vault

echo.
echo ============================================
echo All processes started!
echo ============================================
echo.
echo Running processes:
tasklist | findstr "python"
echo.
echo To stop all processes, run:
echo   taskkill /F /FI "WINDOWTITLE eq Gmail*"
echo   taskkill /F /FI "WINDOWTITLE eq Orchestrator*"
echo.
