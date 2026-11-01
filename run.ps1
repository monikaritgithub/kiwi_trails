<#
.SYNOPSIS
Kiwi Trails Development Launcher
#>

[CmdletBinding()]
param (
    [Parameter(Position = 0)]
    [ValidateSet("all", "install", "backend", "frontend", "seed", "test", "menu")]
    [string]$Task = "all"
)

$RootDir = $PSScriptRoot
Set-Location -Path $RootDir

$PythonExe = Join-Path $RootDir ".venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    $PythonExe = "python"
}

function Ensure-Setup {
    if (-not (Test-Path (Join-Path $RootDir ".venv\Scripts\python.exe"))) {
        Write-Host "Setting up Python virtual environment (.venv)..." -ForegroundColor Yellow
        python -m venv (Join-Path $RootDir ".venv")
        $script:PythonExe = Join-Path $RootDir ".venv\Scripts\python.exe"
        & $PythonExe -m pip install --upgrade pip
        & $PythonExe -m pip install -r (Join-Path $RootDir "requirements.txt")
    }

    if (-not (Test-Path (Join-Path $RootDir ".env"))) {
        if (Test-Path (Join-Path $RootDir ".env.example")) {
            Copy-Item (Join-Path $RootDir ".env.example") (Join-Path $RootDir ".env")
        }
    }

    $needSeed = -not (Test-Path (Join-Path $RootDir "db.sqlite3"))
    & $PythonExe manage.py migrate --noinput
    if ($needSeed) {
        Write-Host "Seeding database..." -ForegroundColor Green
        & $PythonExe manage.py seed_all
    }
}

function Start-Both {
    Clear-Host
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host "       STARTING KIWI TRAILS FRONTEND AND BACKEND   " -ForegroundColor Cyan
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host ""
    
    Ensure-Setup

    Write-Host "Launching Backend on http://127.0.0.1:8000/ ..." -ForegroundColor Green
    Start-Process (Join-Path $RootDir "start_backend.bat")

    Write-Host "Launching Frontend on http://127.0.0.1:5500/frontend/ ..." -ForegroundColor Green
    Start-Process (Join-Path $RootDir "start_frontend.bat")

    Start-Sleep -Seconds 2
    Write-Host "Opening browser at http://127.0.0.1:5500/frontend/ ..." -ForegroundColor Cyan
    Start-Process "http://127.0.0.1:5500/frontend/"

    Write-Host "`n===================================================" -ForegroundColor Cyan
    Write-Host "       KIWI TRAILS RUNNING SUCCESSFULLY!           " -ForegroundColor Green
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host "  Frontend:     http://127.0.0.1:5500/frontend/"
    Write-Host "  Backend API:  http://127.0.0.1:8000/api/v1/"
    Write-Host "  Django Admin: http://127.0.0.1:8000/django-admin/"
    Write-Host ""
    Write-Host "  Test accounts: admin@kiwitrails.test / Password123!"
    Write-Host "                 aroha@kiwitrails.test / Password123!"
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
        "2" { Ensure-Setup }
        "3" { Start-Process (Join-Path $RootDir "start_backend.bat") }
        "4" { Start-Process (Join-Path $RootDir "start_frontend.bat") }
        "5" { & $PythonExe manage.py migrate; & $PythonExe manage.py seed_all }
        "6" { & $PythonExe manage.py test }
        "7" { exit 0 }
        default { Show-Menu }
    }
}

switch ($Task) {
    "all" { Start-Both }
    "install" { Ensure-Setup }
    "backend" { Start-Process (Join-Path $RootDir "start_backend.bat") }
    "frontend" { Start-Process (Join-Path $RootDir "start_frontend.bat") }
    "seed" { & $PythonExe manage.py migrate; & $PythonExe manage.py seed_all }
    "test" { & $PythonExe manage.py test }
    "menu" { Show-Menu }
    default { Start-Both }
}
