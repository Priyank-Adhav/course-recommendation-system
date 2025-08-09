#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

# tools
command -v python3 >/dev/null || { echo "python3 not found"; exit 1; }
command -v npm >/dev/null || { echo "npm not found"; exit 1; }

# backend venv + deps
if [ ! -d "backend/.venv" ]; then python3 -m venv backend/.venv; fi
PY="backend/.venv/bin/python"; PIP="backend/.venv/bin/pip"
$PIP install --upgrade pip >/dev/null
[ -f backend/requirements.txt ] && $PIP install -r backend/requirements.txt

# seed once (first run)
DB="backend/quiz_system.db"
if [ ! -f "$DB" ]; then
  echo "Seeding database..."
  ( cd backend && exec "$PY" seed_data.py )
fi

# start backend
echo "Starting backend http://localhost:5000"
( cd backend && exec "$PY" app.py ) & BACK_PID=$!

# frontend
echo "Installing frontend deps (if needed)..."
( cd frontend-vite && npm install >/dev/null )
echo "Starting frontend http://localhost:5173"
( cd frontend-vite && exec npm run dev ) & FRONT_PID=$!

trap 'echo; echo "Shutting down..."; kill $BACK_PID $FRONT_PID 2>/dev/null || true' INT TERM
wait