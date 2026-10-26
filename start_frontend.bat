@echo off
title Kiwi Trails Frontend (Port 5500)
cd /d "%~dp0"
set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python"
echo ===================================================
echo             KIWI TRAILS FRONTEND
echo ===================================================
echo.
echo Running at: http://127.0.0.1:5500/frontend/
echo.
echo Press Ctrl+C to stop the server.
echo.
"%PYTHON_EXE%" serve_frontend.py
echo.
pause
