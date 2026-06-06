@echo off
cd /d "%~dp0"
echo Starting server at http://localhost:8000
start http://localhost:8000
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0serve.ps1"
pause
