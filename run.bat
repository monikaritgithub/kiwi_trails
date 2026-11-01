@echo off
setlocal enabledelayedexpansion
title Kiwi Trails Launcher

cd /d "%~dp0"

set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"

set "CMD_ARG=%~1"
if /i "%CMD_ARG%"=="menu" goto menu
if not "%CMD_ARG%"=="" goto handle_arg

:auto_start
cls
echo ===================================================
echo        KIWI TRAILS - SINGLE CLICK LAUNCHER
echo ===================================================
echo.
echo Initializing environment and services...
echo.

rem Step 1: Check Python and Virtual Environment
if not exist "%PYTHON_EXE%" (
    echo [1/5] Virtual environment (.venv) not found. Setting up...
    python --version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Python is not found in system PATH.
        echo Please install Python 3.10+ from python.org and add it to PATH.
        pause
        exit /b 1
    )
    echo       Creating virtual environment...
    python -m venv "%~dp0.venv"
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
    echo [2/5] Installing dependencies from requirements.txt...
    "%PYTHON_EXE%" -m pip install --upgrade pip >nul 2>&1
    "%PYTHON_EXE%" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies.
        pause
        exit /b 1
    )
) else (
    echo [1/5] Virtual environment verified (.venv).
    echo [2/5] Dependencies verified.
)

rem Step 2: Environment file
if not exist "%~dp0.env" (
    if exist "%~dp0.env.example" (
        echo [3/5] Setting up local configuration (.env)...
        copy "%~dp0.env.example" "%~dp0.env" >nul
    )
) else (
    echo [3/5] Local configuration verified (.env).
)

rem Step 3: Database and Seeding
set "NEED_SEED=0"
if not exist "%~dp0db.sqlite3" (
    set "NEED_SEED=1"
)

echo [4/5] Applying database migrations...
"%PYTHON_EXE%" manage.py migrate --noinput >nul 2>&1

if "%NEED_SEED%"=="1" (
    echo       Seeding fresh demo database (tours, departures, guides, bookings)...
    "%PYTHON_EXE%" manage.py seed_all >nul 2>&1
)
echo [5/5] Database is ready and up to date.

echo.
echo ===================================================
echo        STARTING KIWI TRAILS APPLICATIONS
echo ===================================================
echo.
echo Starting Backend API server on http://127.0.0.1:8000/ ...
start "" "%~dp0start_backend.bat"

echo Starting Frontend server on http://127.0.0.1:5500/frontend/ ...
start "" "%~dp0start_frontend.bat"

echo.
echo Opening Kiwi Trails web application in default browser...
ping 127.0.0.1 -n 3 >nul
start http://127.0.0.1:5500/frontend/

cls
echo ===================================================
echo       KIWI TRAILS IS RUNNING SUCCESSFULLY!
echo ===================================================
echo.
echo   Frontend Application: http://127.0.0.1:5500/frontend/
echo   Backend REST API:     http://127.0.0.1:8000/api/v1/
echo   Django Admin Panel:   http://127.0.0.1:8000/django-admin/
echo.
echo   Default Test Accounts (Password: Password123!):
echo     - Administrator:    admin@kiwitrails.test
echo     - Customer:         aroha@kiwitrails.test
echo     - Customer:         tane@kiwitrails.test
echo.
echo ===================================================
echo Both servers are running in background console windows.
echo To stop servers, close their terminal windows.
echo Press any key to exit this launcher window...
pause >nul
exit /b 0

:handle_arg
if /i "%CMD_ARG%"=="all" goto auto_start
if /i "%CMD_ARG%"=="both" goto auto_start
if /i "%CMD_ARG%"=="dev" goto auto_start
if /i "%CMD_ARG%"=="run" goto auto_start
if /i "%CMD_ARG%"=="install" goto install_packages
if /i "%CMD_ARG%"=="setup" goto install_packages
if /i "%CMD_ARG%"=="backend" goto run_backend
if /i "%CMD_ARG%"=="frontend" goto run_frontend
if /i "%CMD_ARG%"=="seed" goto run_seed
if /i "%CMD_ARG%"=="test" goto run_tests
if /i "%CMD_ARG%"=="tests" goto run_tests
echo Unknown argument: %CMD_ARG%
echo Valid arguments: menu, all, install, backend, frontend, seed, test
pause
exit /b 1

:menu
cls
echo ===================================================
echo               KIWI TRAILS LAUNCHER
echo ===================================================
echo.
echo   [1] Run Both Frontend and Backend (Recommended)
echo   [2] Install Packages and Setup Environment
echo   [3] Run Backend Only  (Django on Port 8000)
echo   [4] Run Frontend Only (HTTP on Port 5500)
echo   [5] Run Migrations and Seed Database
echo   [6] Run Full Test Suite
echo   [7] Exit
echo.
echo ===================================================
set /p choice="Select an option (1-7): "

if "%choice%"=="1" goto auto_start
if "%choice%"=="2" goto install_packages
if "%choice%"=="3" goto run_backend
if "%choice%"=="4" goto run_frontend
if "%choice%"=="5" goto run_seed
if "%choice%"=="6" goto run_tests
if "%choice%"=="7" exit /b 0

echo Invalid option. Please try again.
pause
goto menu

:install_packages
cls
echo ===================================================
echo           INSTALLING PACKAGES AND SETUP
echo ===================================================
echo.
if not exist "%PYTHON_EXE%" (
    echo Creating virtual environment (.venv)...
    python -m venv "%~dp0.venv"
    set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
)
echo Upgrading pip and installing required packages...
"%PYTHON_EXE%" -m pip install --upgrade pip
"%PYTHON_EXE%" -m pip install -r requirements.txt
if not exist "%~dp0.env" (
    if exist "%~dp0.env.example" (
        copy "%~dp0.env.example" "%~dp0.env"
    )
)
"%PYTHON_EXE%" manage.py migrate
echo Setup complete!
if "%CMD_ARG%"=="" pause
goto end

:run_backend
start "" "%~dp0start_backend.bat"
goto end

:run_frontend
start "" "%~dp0start_frontend.bat"
ping 127.0.0.1 -n 2 >nul
start http://127.0.0.1:5500/frontend/
goto end

:run_seed
cls
echo Seeding database...
"%PYTHON_EXE%" manage.py migrate
"%PYTHON_EXE%" manage.py seed_all
echo Seeding complete!
if "%CMD_ARG%"=="" pause
goto end

:run_tests
cls
echo Running test suite...
"%PYTHON_EXE%" manage.py test
if "%CMD_ARG%"=="" pause
goto end

:end
exit /b 0
