@echo off
setlocal enabledelayedexpansion
title Kiwi Trails Launcher

cd /d "%~dp0"

set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" (
    set "PYTHON_EXE=python"
)

set "CMD_ARG=%~1"
if not "%CMD_ARG%"=="" goto handle_arg

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

if "%choice%"=="1" goto run_both
if "%choice%"=="2" goto install_packages
if "%choice%"=="3" goto run_backend
if "%choice%"=="4" goto run_frontend
if "%choice%"=="5" goto run_seed
if "%choice%"=="6" goto run_tests
if "%choice%"=="7" goto end

echo Invalid option. Please try again.
pause
goto menu

:handle_arg
if /i "%CMD_ARG%"=="all" goto run_both
if /i "%CMD_ARG%"=="both" goto run_both
if /i "%CMD_ARG%"=="dev" goto run_both
if /i "%CMD_ARG%"=="install" goto install_packages
if /i "%CMD_ARG%"=="setup" goto install_packages
if /i "%CMD_ARG%"=="backend" goto run_backend
if /i "%CMD_ARG%"=="frontend" goto run_frontend
if /i "%CMD_ARG%"=="seed" goto run_seed
if /i "%CMD_ARG%"=="test" goto run_tests
if /i "%CMD_ARG%"=="tests" goto run_tests
echo Unknown argument: %CMD_ARG%
echo Valid arguments: all, install, backend, frontend, seed, test
pause
goto end

:install_packages
cls
echo ===================================================
echo           INSTALLING PACKAGES AND SETUP
echo ===================================================
echo.
if not exist "%~dp0.venv\Scripts\python.exe" (
    echo Creating virtual environment (.venv)...
    python -m venv "%~dp0.venv"
    if errorlevel 1 (
        echo Error creating virtual environment. Please ensure Python is installed and added to PATH.
        pause
        goto menu
    )
    set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
)

echo Upgrading pip and installing required packages...
"%PYTHON_EXE%" -m pip install --upgrade pip
"%PYTHON_EXE%" -m pip install -r requirements.txt
if errorlevel 1 (
    echo Error installing packages.
    pause
    goto menu
)

if not exist "%~dp0.env" (
    if exist "%~dp0.env.example" (
        echo Creating .env file from .env.example...
        copy "%~dp0.env.example" "%~dp0.env"
    )
)

echo.
echo Applying database migrations...
"%PYTHON_EXE%" manage.py migrate
echo.
echo Packages installed and environment ready!
echo.
if "%CMD_ARG%"=="" (
    pause
    goto menu
)
goto end

:run_both
cls
echo ===================================================
echo        STARTING KIWI TRAILS FRONTEND AND BACKEND
echo ===================================================
echo.
if not exist "%PYTHON_EXE%" (
    echo Python executable not found. Running install first...
    goto install_packages
)

echo Starting Backend on http://127.0.0.1:8000/ ...
start "" "%~dp0start_backend.bat"

echo Starting Frontend on http://127.0.0.1:5500/frontend/ ...
start "" "%~dp0start_frontend.bat"

echo.
echo Opening browser to http://127.0.0.1:5500/frontend/ ...
ping 127.0.0.1 -n 3 >nul
start http://127.0.0.1:5500/frontend/

echo.
echo Both servers are running in separate console windows.
echo To stop a server, close its window or press Ctrl+C in it.
echo.
if "%CMD_ARG%"=="" (
    pause
    goto menu
)
goto end

:run_backend
start "" "%~dp0start_backend.bat"
if "%CMD_ARG%"=="" goto menu
goto end

:run_frontend
start "" "%~dp0start_frontend.bat"
ping 127.0.0.1 -n 2 >nul
start http://127.0.0.1:5500/frontend/
if "%CMD_ARG%"=="" goto menu
goto end

:run_seed
cls
echo ===================================================
echo              SEEDING DATABASE
echo ===================================================
echo.
"%PYTHON_EXE%" manage.py migrate
"%PYTHON_EXE%" manage.py seed_all
echo.
if "%CMD_ARG%"=="" (
    pause
    goto menu
)
goto end

:run_tests
cls
echo ===================================================
echo               RUNNING TESTS
echo ===================================================
echo.
"%PYTHON_EXE%" manage.py test
echo.
if "%CMD_ARG%"=="" (
    pause
    goto menu
)
goto end

:end
exit /b 0
