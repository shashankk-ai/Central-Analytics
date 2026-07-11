# Scimplify Central Analytics Platform

Live operational intelligence platform for Scimplify (Cocreate Global
Technologies Pvt. Ltd.) leadership. See `docs/` for phase completion records.

## Structure

```
frontend/   React + TypeScript + Vite + Tailwind + shadcn/ui
backend/    Python + FastAPI + pandas
docs/       Phase completion records
```

## Running locally

**Backend**

```
cd backend
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env   # fill in Zoho OAuth credentials
.venv/bin/uvicorn app.main:app --reload --port 8000
```

**Frontend**

```
cd frontend
npm install
npm run dev
```

The Vite dev server proxies `/api` to `http://localhost:8000`.

## Tests

```
cd backend
.venv/bin/pytest
```
