<#
.SYNOPSIS
Kiwi Trails Development Launcher
#>

[CmdletBinding()]
param (
    [Parameter(Position = 0)]
    [ValidateSet("all", "install", "backend", "frontend", "seed", "test", "menu")]
    [string]$Task = "menu"
)

$RootDir = $PSScriptRoot
Set-Location -Path $RootDir

$PythonExe = Join-Path $RootDir ".venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    $PythonExe = "python"
}

function Show-Menu {
    Clear-Host
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host "               KIWI TRAILS LAUNCHER                " -ForegroundColor Cyan
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  [1] Run Both Frontend and Backend (Recommended)"
    Write-Host "  [2] Install Packages and Setup Environment"
    Write-Host "  [3] Run Backend Only  (Django on Port 8000)"
    Write-Host "  [4] Run Frontend Only (HTTP on Port 5500)"
    Write-Host "  [5] Run Migrations and Seed Database"
    Write-Host "  [6] Run Full Test Suite"
    Write-Host "  [7] Exit"
    Write-Host ""
    Write-Host "===================================================" -ForegroundColor Cyan
    $choice = Read-Host "Select an option (1-7)"
    switch ($choice) {
        "1" { Start-Both }
        "2" { Install-Packages }
        "3" { Start-Backend }
        "4" { Start-Frontend }
        "5" { Run-Seed }
        "6" { Run-Tests }
        "7" { exit 0 }
        default {
            Write-Host "Invalid choice. Please select 1 through 7." -ForegroundColor Yellow
            Start-Sleep -Seconds 2
            Show-Menu
        }
    }
}

function Install-Packages {
    Clear-Host
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host "          INSTALLING PACKAGES AND SETUP            " -ForegroundColor Cyan
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host ""
    if (-not (Test-Path (Join-Path $RootDir ".venv\Scripts\python.exe"))) {
        Write-Host "Creating virtual environment (.venv)..." -ForegroundColor Yellow
        python -m venv (Join-Path $RootDir ".venv")
        $script:PythonExe = Join-Path $RootDir ".venv\Scripts\python.exe"
    }

    Write-Host "Upgrading pip and installing dependencies..." -ForegroundColor Green
    & $PythonExe -m pip install --upgrade pip
    & $PythonExe -m pip install -r (Join-Path $RootDir "requirements.txt")

    if (-not (Test-Path (Join-Path $RootDir ".env"))) {
        if (Test-Path (Join-Path $RootDir ".env.example")) {
            Write-Host "Creating .env from .env.example..." -ForegroundColor Green
            Copy-Item (Join-Path $RootDir ".env.example") (Join-Path $RootDir ".env")
        }
    }

    Write-Host "Applying database migrations..." -ForegroundColor Green
    & $PythonExe manage.py migrate

    Write-Host "`nSetup complete! Packages are installed and database is migrated." -ForegroundColor Green
    if ($Task -eq "menu") {
        Read-Host "`nPress Enter to return to menu..."
        Show-Menu
    }
}

function Start-Both {
    Clear-Host
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host "       STARTING KIWI TRAILS FRONTEND AND BACKEND   " -ForegroundColor Cyan
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Launching Backend on http://127.0.0.1:8000/ ..." -ForegroundColor Green
    Start-Process (Join-Path $RootDir "start_backend.bat")

    Write-Host "Launching Frontend on http://127.0.0.1:5500/frontend/ ..." -ForegroundColor Green
    Start-Process (Join-Path $RootDir "start_frontend.bat")

    Start-Sleep -Seconds 2
    Write-Host "Opening browser at http://127.0.0.1:5500/frontend/ ..." -ForegroundColor Cyan
    Start-Process "http://127.0.0.1:5500/frontend/"

    Write-Host "`nBoth servers are running in separate windows." -ForegroundColor Green
    Write-Host "Press Ctrl+C or close the window to stop a server."
    if ($Task -eq "menu") {
        Read-Host "`nPress Enter to return to menu..."
        Show-Menu
    }
}

function Start-Backend {
    Write-Host "Launching Backend on http://127.0.0.1:8000/ ..." -ForegroundColor Green
    Start-Process (Join-Path $RootDir "start_backend.bat")
    if ($Task -eq "menu") { Show-Menu }
}

function Start-Frontend {
    Write-Host "Launching Frontend on http://127.0.0.1:5500/frontend/ ..." -ForegroundColor Green
    Start-Process (Join-Path $RootDir "start_frontend.bat")
    Start-Sleep -Seconds 1
    Start-Process "http://127.0.0.1:5500/frontend/"
    if ($Task -eq "menu") { Show-Menu }
}

function Run-Seed {
    Clear-Host
    Write-Host "Seeding database..." -ForegroundColor Green
    & $PythonExe manage.py migrate
    & $PythonExe manage.py seed_all
    if ($Task -eq "menu") {
        Read-Host "`nPress Enter to return to menu..."
        Show-Menu
    }
}

function Run-Tests {
    Clear-Host
    Write-Host "Running tests..." -ForegroundColor Green
    & $PythonExe manage.py test
    if ($Task -eq "menu") {
        Read-Host "`nPress Enter to return to menu..."
        Show-Menu
    }
}

switch ($Task) {
    "all" { Start-Both }
    "install" { Install-Packages }
    "backend" { Start-Backend }
    "frontend" { Start-Frontend }
    "seed" { Run-Seed }
    "test" { Run-Tests }
    default { Show-Menu }
}
