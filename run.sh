#!/usr/bin/env bash
# Kiwi Trails Single-Click / Single-Command Launcher for macOS & Linux

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "==================================================="
echo "       KIWI TRAILS - APPLICATION LAUNCHER         "
echo "==================================================="
echo ""

# Virtual Environment Setup
if [ ! -d ".venv" ]; then
    echo "[1/4] Setting up Python virtual environment (.venv)..."
    python3 -m venv .venv
    .venv/bin/pip install --upgrade pip > /dev/null 2>&1
    .venv/bin/pip install -r requirements.txt
else
    echo "[1/4] Virtual environment verified (.venv)."
fi

# Environment Configuration
if [ ! -f ".env" ]; then
    echo "[2/4] Setting up local configuration (.env)..."
    cp .env.example .env
fi

# Migrations & Seeding
NEED_SEED=0
if [ ! -f "db.sqlite3" ]; then
    NEED_SEED=1
fi

echo "[3/4] Applying database migrations..."
.venv/bin/python manage.py migrate --noinput > /dev/null 2>&1

if [ "$NEED_SEED" -eq 1 ]; then
    echo "      Seeding database..."
    .venv/bin/python manage.py seed_all > /dev/null 2>&1
fi

echo "[4/4] Starting services..."
echo "      Backend:  http://127.0.0.1:8000/"
echo "      Frontend: http://127.0.0.1:5500/frontend/"
echo ""

# Start backend in background
.venv/bin/python manage.py runserver 127.0.0.1:8000 &
BACKEND_PID=$!

# Start frontend in background
.venv/bin/python serve_frontend.py &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM EXIT

sleep 2

# Open browser
if which xdg-open > /dev/null; then
    xdg-open "http://127.0.0.1:5500/frontend/" > /dev/null 2>&1 &
elif which open > /dev/null; then
    open "http://127.0.0.1:5500/frontend/" > /dev/null 2>&1 &
fi

echo "==================================================="
echo "       KIWI TRAILS IS RUNNING SUCCESSFULLY!        "
echo "==================================================="
echo "  Frontend Application: http://127.0.0.1:5500/frontend/"
echo "  Backend API:          http://127.0.0.1:8000/api/v1/"
echo "  Django Admin:         http://127.0.0.1:8000/django-admin/"
echo ""
echo "  Test Login (Password: Password123!):"
echo "    - Admin:    admin@kiwitrails.test"
echo "    - Customer: aroha@kiwitrails.test"
echo "==================================================="
echo "Press Ctrl+C to stop both servers."

wait
