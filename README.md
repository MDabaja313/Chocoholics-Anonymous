# ChocAn Data Processing System (Chocoholics Anonymous)
An organized **localhost** ChocAn Data Processing System web app that implements the professor’s ChocAn requirements: provider workflow, manager workflow, weekly accounting procedure, report generation, and Acme simulation.

## Repo structure
- `backend/`: **FastAPI + SQLite + SQLAlchemy** (Pydantic validation, RBAC, HTTP-only cookie sessions)
- `frontend/`: **React + Vite + TypeScript** (React Router, dashboard layout)
- `generated_reports/`: generated `.txt` reports (not committed)
- `chocan/`: legacy Flask/JSON prototype (kept for reference; not the advertised stack)

## Stack (actual)
- **Frontend**: React, Vite, TypeScript, React Router
- **Backend**: FastAPI, SQLite, SQLAlchemy ORM, Pydantic
- **Auth**: hashed passwords + **HTTP-only cookie** sessions
- **Reports**: plain `.txt` files saved locally in `generated_reports/`

## Demo credentials (seeded)
- **admin / admin123**
- **provider1 / provider123**
- **manager / manager123**

## Setup & run (Windows / PowerShell)
Open **two terminals** at the repo root.

### Backend
```powershell
python -m venv backend\.venv
backend\.venv\Scripts\python -m pip install -r backend\requirements.txt

# Reset + seed database
backend\.venv\Scripts\python -m backend.app.seed --reset

# Run API
backend\.venv\Scripts\uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8001
```

Health: `http://127.0.0.1:8001/api/health`

### Frontend
```powershell
cd frontend
npm install
npm run dev
```

Open: `http://127.0.0.1:5173/`

## Run tests
```powershell
backend\.venv\Scripts\pytest
```

## Tested flows (primary goal)
### Provider flow
Login → Validate Member → Bill a Service → View Submitted Services

### Manager flow
Login → Run Weekly Reports → Download Member / Provider / Summary / EFT files

### Acme simulation flow
Suspend member → Reinstate member → Confirm status change in member records

## Pages
### Public
- Login (`/login`)

### Provider
- Validate Member (`/provider/validate`)
- Bill Service (`/provider/bill`)
- Provider Directory (`/provider/directory`)
- My Submitted Services (`/provider/services`)

### Manager
- Members (`/manager/members`)
- Providers (`/manager/providers`)
- Services (`/manager/services`)
- Weekly Reports + downloads (`/manager/reports`)
- Acme Simulation (`/manager/acme`)

### Admin
- Admin can access provider + manager features.

## Report generation
- Weekly report files are written to `generated_reports/`
- Download them from **Manager → Weekly Reports**
- Provider Directory file can be generated from the master services list via `POST /api/directory/generate`

## Screenshot checklist
- Login page + successful login for provider, manager, admin
- Provider: Validate Member (active vs suspended), Bill Service (fee shown), My Submitted Services
- Manager: Weekly Reports page + open/download `Summary_YYYY-MM-DD.txt` and `EFT_YYYY-MM-DD.txt`
- Manager: Acme Simulation suspend/reinstate + Members page showing changed status

## Known limitations
- Manager CRUD pages currently focus on create/delete + quick status toggles; full “edit all fields” forms can be added next.
