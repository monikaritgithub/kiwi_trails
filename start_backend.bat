@echo off
title Kiwi Trails Backend (Port 8000)
cd /d "%~dp0"
set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python"
echo ===================================================
echo     KIWI TRAILS BACKEND (DJANGO REST API)
echo ===================================================
echo.
echo Running at: http://127.0.0.1:8000/
echo Admin panel: http://127.0.0.1:8000/admin/
echo API root:    http://127.0.0.1:8000/api/v1/
echo.
echo Press Ctrl+C to stop the server.
echo.
"%PYTHON_EXE%" manage.py runserver 127.0.0.1:8000
echo.
pause
