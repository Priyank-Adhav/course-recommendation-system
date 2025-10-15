#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

# tools
command -v python3 >/dev/null || { echo "python3 not found"; exit 1; }
command -v npm >/dev/null || { echo "npm not found"; exit 1; }

# backend venv + deps
cd backend
if [ ! -d ".venv" ]; then python3 -m venv .venv; fi
.venv/bin/pip install --upgrade pip >/dev/null
[ -f requirements.txt ] && .venv/bin/pip install -r requirements.txt
DB="quiz_system.db"

# seed once (first run)
if [ ! -f "$DB" ]; then
  echo "Seeding database..."
  .venv/bin/python seed_data.py
fi

# start backend
echo "Starting backend http://localhost:5000"
.venv/bin/python app.py & BACK_PID=$!
cd ..

# frontend
echo "Installing frontend deps (if needed)..."
( cd frontend-vite && npm install >/dev/null )
echo "Starting frontend http://localhost:5173"
( cd frontend-vite && exec npm run dev ) & FRONT_PID=$!

trap 'echo; echo "Shutting down..."; kill $BACK_PID $FRONT_PID 2>/dev/null || true' INT TERM
wait
