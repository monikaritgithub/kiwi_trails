@echo off
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
if exist "%PYTHON_EXE%" goto venv_exists

echo [1/5] Setting up virtual environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Python was not found in system PATH.
    echo Please install Python 3.10+ from python.org and check "Add Python to PATH".
    echo.
    pause
    exit /b 1
)

python -m venv "%~dp0.venv"
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to create virtual environment in %~dp0.venv
    echo.
    pause
    exit /b 1
)

echo [2/5] Installing dependencies from requirements.txt...
"%PYTHON_EXE%" -m pip install --upgrade pip >nul 2>&1
"%PYTHON_EXE%" -m pip install -r "%~dp0requirements.txt"
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install packages from requirements.txt
    echo.
    pause
    exit /b 1
)
goto venv_ready

:venv_exists
echo [1/5] Virtual environment verified.
echo [2/5] Dependencies verified.

:venv_ready
rem Step 2: Environment file
if exist "%~dp0.env" goto env_exists
if exist "%~dp0.env.example" (
    echo [3/5] Setting up configuration file .env...
    copy "%~dp0.env.example" "%~dp0.env" >nul
)
goto env_ready

:env_exists
echo [3/5] Configuration file verified.

:env_ready
rem Step 3: Database and Seeding
set "NEED_SEED=0"
if not exist "%~dp0db.sqlite3" set "NEED_SEED=1"

echo [4/5] Applying database migrations...
"%PYTHON_EXE%" "%~dp0manage.py" migrate --noinput >nul 2>&1

if "%NEED_SEED%"=="1" (
    echo       Seeding fresh demo database...
    "%PYTHON_EXE%" "%~dp0manage.py" seed_all >nul 2>&1
)
echo [5/5] Database is ready and up to date.

echo.
echo ===================================================
echo        STARTING KIWI TRAILS APPLICATIONS
echo ===================================================
echo.
echo Starting Backend API server on http://127.0.0.1:8000/ ...
start "Kiwi Trails Backend (Port 8000)" cmd /k "call "%~dp0start_backend.bat""

echo Starting Frontend server on http://127.0.0.1:5500/frontend/ ...
start "Kiwi Trails Frontend (Port 5500)" cmd /k "call "%~dp0start_frontend.bat""

echo.
echo Opening Kiwi Trails in default web browser...
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
echo.
echo ===================================================
echo Both servers are running in separate terminal windows.
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
"%PYTHON_EXE%" -m pip install -r "%~dp0requirements.txt"
if not exist "%~dp0.env" (
    if exist "%~dp0.env.example" (
        copy "%~dp0.env.example" "%~dp0.env" >nul
    )
)
"%PYTHON_EXE%" "%~dp0manage.py" migrate
echo Setup complete!
if "%CMD_ARG%"=="" pause
goto end

:run_backend
start "Kiwi Trails Backend (Port 8000)" cmd /k "call "%~dp0start_backend.bat""
goto end

:run_frontend
start "Kiwi Trails Frontend (Port 5500)" cmd /k "call "%~dp0start_frontend.bat""
ping 127.0.0.1 -n 2 >nul
start http://127.0.0.1:5500/frontend/
goto end

:run_seed
cls
echo Seeding database...
"%PYTHON_EXE%" "%~dp0manage.py" migrate
"%PYTHON_EXE%" "%~dp0manage.py" seed_all
echo Seeding complete!
if "%CMD_ARG%"=="" pause
goto end

:run_tests
cls
echo Running test suite...
"%PYTHON_EXE%" "%~dp0manage.py" test
if "%CMD_ARG%"=="" pause
goto end

:end
exit /b 0
