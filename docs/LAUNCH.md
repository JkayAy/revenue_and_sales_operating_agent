# Local Launch

## Prerequisites

- Python 3.11+  
- Node 20+ (dashboard)  
- Docker Desktop (optional Postgres)

---

## Quick start (host)

```powershell
cd "c:\Users\jkay5\Desktop\AI Agents\revenue and sales operations agent"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt

pytest
python -m eval

sales-api
# API: http://127.0.0.1:8000
# Docs: http://127.0.0.1:8000/docs
```

**Dashboard** (second terminal):

```powershell
cd apps\dashboard
npm install
$env:NEXT_PUBLIC_SALES_API="http://127.0.0.1:8000"
npm run dev
# http://localhost:3000
```

---

## Docker (Postgres + API)

```powershell
.\scripts\docker-up.ps1 -Build
curl http://localhost:8000/ready
```

API persists leads to Postgres when `DATABASE_URL` is set (automatic in Compose). Host-run API: use `.env` with `DATABASE_URL=postgresql://sales:sales@127.0.0.1:5434/sales_agent`.

---

## Sample ingest

```powershell
curl -X POST http://127.0.0.1:8000/v1/leads/ingest `
  -H "Content-Type: application/json" `
  -d '{"email":"alex@acme.io","first_name":"Alex","company":"Acme Analytics","employee_count":120,"country":"US","industry":"software"}'
```

---

## Environment

Copy `.env.example` to `.env` and set `ADMIN_API_KEY` for admin routes.
