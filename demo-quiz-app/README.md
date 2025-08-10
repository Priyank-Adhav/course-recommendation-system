# 🎯 **Demo Quiz App**  

A sleek, modern quiz platform with a **Flask + SQLite** backend and a **Vite + React + TypeScript** frontend, styled using **Tailwind CSS** and **shadcn/ui**.  
Includes **Dark Mode**, a **polished UI**, and a **one-command startup** for instant development.

---

## 🏅 **Badges**
**Frontend:** React 19 · TypeScript · Vite · Tailwind 3 · shadcn/ui · Radix · Lucide  
**Backend:** Flask · SQLite  
**Dev:** Node 18+ · Python 3.10+

---

## 📜 **Table of Contents**
1. [✨ Highlights](#-highlights)
2. [🛠 Tech Stack](#-tech-stack)
3. [📂 Project Structure](#-project-structure)
4. [⚡ Quick Start](#-quick-start)
5. [🌍 Environment](#-environment)
6. [📡 API Overview](#-api-overview)
7. [🎨 Frontend Details](#-frontend-details)
8. [📜 Development Scripts](#-development-scripts)
9. [🌱 Seeding](#-seeding)
10. [🐞 Troubleshooting](#-troubleshooting)

---

## ✨ **Highlights**
- 🎯 **Clean UX** — Gradient hero, card grid, filters/search/sort, sticky progress bar, review & submit dialogs  
- 🌙 **Dark Mode** — Class-based theme with accessible focus states  
- 🚀 **One-Command Dev** — Start both frontend & backend and auto-seed DB on first run  

---

## 🛠 **Tech Stack**
- **Frontend:** React 19, TypeScript, Vite, Tailwind CSS 3, shadcn/ui (Radix), Lucide icons  
- **Backend:** Flask (Python 3), SQLite (file-based DB)  
- **Misc:** CORS enabled, LocalStorage for demo user  

---

## 📂 **Project Structure**
```
demo-quiz-app/
├── backend/                  # Flask API + SQLite
│   ├── app.py                 # Entry point
│   ├── database.py            # DB initialization
│   ├── routes/                # API routes
│   ├── models/                # ORM models
│   ├── seed_data.py           # DB seeding script
│   └── tests/                 # Unit tests
├── frontend/                  # Legacy CRA (reference only)
├── frontend-vite/             # New Vite + React + TS frontend
│   ├── src/                   # Components, pages, services
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── postcss.config.js
├── dev.sh                     # Start both servers, auto-seed
└── README.md                  # Documentation
```

---

## ⚡ **Quick Start**

### **Prerequisites**
- Python **3.10+**
- Node.js **18+**
- npm

**Option A — One Command (Recommended)**  
```bash
chmod +x ./dev.sh
./dev.sh
```
- **Frontend:** http://localhost:5173  
- **Backend:** http://localhost:5000  

**Option B — Manual Setup**  
_Backend:_  
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # Windows: .\.venv\Scripts\activate
pip install -r requirements.txt
python seed_data.py
python app.py
```
_Frontend:_  
```bash
cd ../frontend-vite
npm install
echo "VITE_API_BASE=http://localhost:5000" > .env
npm run dev
```

---

## 🌍 **Environment Variables**
**Frontend (`frontend-vite/.env`)**  
```
VITE_API_BASE=http://localhost:5000
```
**Backend:**  
- SQLite DB Path: `backend/quiz_system.db` (configured in `database.py`)

---

## 📡 **API Overview**
**Base URL:** `http://localhost:5000`  

**Endpoints:**  
- **Users:**  
  - `POST /register` — Register user  
  - `POST /users` — Create user  
- **Categories:**  
  - `GET /categories` — List  
  - `POST /categories` — Create  
- **Quizzes:**  
  - `GET /quizzes` — List  
  - `POST /quizzes` — Create  
- **Questions:**  
  - `GET /questions/:quiz_id` — Get questions  
  - `POST /questions` — Add question(s)  
- **Submit/Results:**  
  - `POST /submit` — Submit answers  
  - `GET /results/:user_id` — User results  
  - `GET /result_details/:result_id` — Per-question details  
- **Utility:**  
  - `POST /clear_all` — Clear all data (dangerous)  

---

## 🎨 **Frontend Details**
- **Styling:** Tailwind utilities + shadcn/ui primitives  
- **Theme:** Cyan–blue palette via CSS variables  
- **Dark Mode:** Toggles `dark` class on `<html>`  
- **Pages:**  
  - Home — Aurora gradient hero, stats, highlights  
  - Quiz List — Search, category chips, sort, animated cards  
  - Quiz — Sticky progress, “radio cards”, review panel, submit dialog  
  - Results — Score hero, detailed breakdown  
  - My Results — Summary cards, recent results

---

## 📜 **Development Scripts**
**Backend:**  
```bash
pip install -r requirements.txt
python app.py
python seed_data.py
```
**Frontend:**  
```bash
npm install
npm run dev
npm run build
npm run preview
npm run lint
```

---

## 🌱 **Seeding**
- **Automatic:** `./dev.sh` (checks if `quiz_system.db` exists)  
- **Manual:**  
```bash
cd backend && python seed_data.py
```

---

## 🐞 **Troubleshooting**
- **Vite Node types error:**  
```bash
npm i -D @types/node
```
- **Port conflicts:**  
  - Backend: Change in `app.py`  
  - Frontend: `npm run dev -- --port 5174`  
- **CORS Issues:** Already enabled in `backend/app.py`

---

**🚀 Ready to build your next interactive quiz experience!**