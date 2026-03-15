@echo off
echo ============================================
echo    AI Employee - Complete System Run
echo ============================================
echo.

echo [1/5] Starting Gmail Watcher...
start "Gmail Watcher" python watchers\gmail_watcher.py AI_Employee_Vault
timeout /t 2 /nobreak >nul

echo [2/5] Starting Gmail Smart Responder...
start "Gmail Smart Responder" python watchers\gmail_smart_responder.py AI_Employee_Vault
timeout /t 2 /nobreak >nul

echo [3/5] Starting Facebook Watcher...
start "Facebook Watcher" python watchers\facebook_watcher.py AI_Employee_Vault
timeout /t 2 /nobreak >nul

echo [4/5] Starting Orchestrator...
start "Orchestrator" python orchestrator.py AI_Employee_Vault
timeout /t 2 /nobreak >nul

echo [5/5] Starting Web Dashboard...
start "Web Dashboard" python web_dashboard\app.py AI_Employee_Vault
timeout /t 3 /nobreak >nul

echo.
echo ============================================
echo    All Components Started!
echo ============================================
echo.
echo Running Components:
echo   ✓ Gmail Watcher
echo   ✓ Gmail Smart Responder
echo   ✓ Facebook Watcher
echo   ✓ Orchestrator
echo   ✓ Web Dashboard
echo.
echo Open Dashboard: http://localhost:7861
echo.
echo To Stop All: taskkill /F /FI "WINDOWTITLE eq*"
echo ============================================
echo.
