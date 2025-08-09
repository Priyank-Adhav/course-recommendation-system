## Demo Quiz App

A modern quiz platform with a Flask + SQLite backend and a Vite + React + TypeScript frontend using Tailwind CSS and shadcn/ui. Dark mode, polished UI, and one-command startup.

### Badges
- **Frontend**: React 19 · TypeScript · Vite · Tailwind 3 · shadcn/ui · Radix · Lucide
- **Backend**: Flask · SQLite
- **Dev**: Node 18+ · Python 3.10+

---

## Table of Contents
- [Highlights](#highlights)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Environment](#environment)
- [API Overview](#api-overview)
- [Frontend Details](#frontend-details)
- [Development Scripts](#development-scripts)
- [Seeding](#seeding)
- [Troubleshooting](#troubleshooting)
- [Screenshots](#screenshots)
- [Roadmap](#roadmap)
- [License](#license)

---

### Highlights
- **Clean UX**: gradient hero, card grid, filters/search/sort, sticky progress, review & submit dialogs
- **Dark mode**: class-based theme; accessible focus states
- **One command**: start frontend + backend and auto-seed on first run

### Tech Stack
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS 3, shadcn/ui (Radix), Lucide icons
- **Backend**: Flask (Python 3), SQLite (file DB)
- **Misc**: CORS enabled, simple local storage for demo user

---

## Project Structure
```
demo-quiz-app/
├── backend/                      # Flask API + SQLite
│   ├── app.py                    # Entry point
│   ├── database.py               # DB init (SQLite file)
│   ├── routes/                   # API routes
│   │   ├── quiz_service.py
│   │   └── user_service.py
│   ├── models/
│   │   └── models.py
│   ├── seed_data.py              # Seed script (first run)
│   ├── requirements.txt
│   └── tests/
│       ├── test_quiz.py
│       └── test_user.py
├── frontend/                     # Legacy CRA (kept for reference)
├── frontend-vite/                # New Vite + React + TS frontend
│   ├── src/
│   │   ├── components/
│   │   │   └── ui/               # shadcn-style primitives
│   │   ├── pages/
│   │   ├── services/
│   │   └── lib/
│   │       └── utils.ts
│   ├── index.html
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── postcss.config.js
├── dev.sh                        # Linux/macOS: start backend+frontend, auto-seed first run
├── .gitignore
└── README.md                     # This file
```
---

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm

### Option A — One command (recommended)
- Linux/macOS:
  - Make executable once:
    - `chmod +x ./dev.sh`
  - Start both servers:
    - `./dev.sh`
  - First run auto-seeds via `backend/seed_data.py`
- Windows (PowerShell):
  - Create `dev.ps1` (see snippet in Troubleshooting if needed)
  - Run:
    - `.\dev.ps1`

- Frontend: `http://localhost:5173`
- Backend:  `http://localhost:5000`

### Option B — Manual

- Backend
  - Create venv and install:
    - `cd backend`
    - `python3 -m venv .venv`
    - `source .venv/bin/activate` (Windows: `.\.venv\Scripts\activate`)
    - `pip install -r requirements.txt`
  - Seed (first time):
    - `python seed_data.py`
  - Run:
    - `python app.py`

- Frontend (Vite)
  - `cd ../frontend-vite`
  - `npm install`
  - optional: `echo "VITE_API_BASE=http://localhost:5000" > .env`
  - `npm run dev`

---

## Environment
- Frontend (`frontend-vite/.env`)
  - **VITE_API_BASE**: Flask API base URL
    ```
    VITE_API_BASE=http://localhost:5000
    ```
- Backend
  - SQLite DB: `backend/quiz_system.db` (configured in `backend/database.py`)

---

## API Overview
Base URL: `http://localhost:5000`

- **Users**
  - POST `/register` — Register user
  - POST `/users` — Create user (simple)
- **Categories**
  - GET `/categories` — List
  - POST `/categories` — Create
- **Quizzes**
  - GET `/quizzes` — List
  - POST `/quizzes` — Create
- **Questions**
  - GET `/questions/:quiz_id` — Get questions
  - POST `/questions` — Add (single or array)
- **Submit/Results**
  - POST `/submit` — Submit answers
  - GET `/results/:user_id` — User results
  - GET `/result_details/:result_id` — Per-question details
- **Utility**
  - POST `/clear_all` — Clear all data (danger)

Response shapes align with `frontend-vite/src/services/api.ts`.

---

## Frontend Details
- **Styling**: Tailwind utilities + shadcn/ui primitives in `src/components/ui/`
- **Brand**: cyan–blue palette via CSS variables in `src/index.css`
- **Dark mode**: toggles `dark` class on `<html>`
- **Pages**:
  - Home: aurora gradient hero, stats, highlights, steps
  - Quiz List: search, category chips with counts, sort, animated cards
  - Quiz: sticky progress, “radio cards”, review panel, submit dialog, keyboard shortcuts (←/→, 1–4)
  - Results: score hero (color tiers), detailed breakdown with badges
  - My Results: summary cards, recent results with score chips

---

## Development Scripts
- Backend:
  - `pip install -r requirements.txt`
  - `python app.py`
  - `python seed_data.py`
- Frontend:
  - `npm install`
  - `npm run dev`
  - `npm run build`
  - `npm run preview`
  - `npm run lint`

---

## Seeding
- Automatic with `./dev.sh` on first run (checks `backend/quiz_system.db`)
- Manual:
  - `cd backend && python seed_data.py`

---

## Troubleshooting
- Node path types error in `vite.config.ts`:
  - `npm i -D @types/node`
  - Use URL API:
    ```
    import { fileURLToPath, URL } from 'node:url'
    resolve: { alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) } }
    ```
- Ports in use:
  - Backend port: change in `backend/app.py`
  - Frontend port: `npm run dev -- --port 5174`
- CORS: enabled in `backend/app.py` via `flask_cors.CORS(app)`

---
