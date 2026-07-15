# Scimplify Central Analytics Platform

Live operational intelligence platform for Scimplify (Cocreate Global
Technologies Pvt. Ltd.) leadership. See `docs/` for phase completion records.

## Structure

```
frontend/   React + TypeScript + Vite + Tailwind + shadcn/ui
backend/    Python + FastAPI + pandas
docs/       Phase completion records
```

## Hands-on preview

**Option A — GitHub Codespaces (recommended, no local setup)**

1. On this branch on GitHub, click **Code → Codespaces → Create codespace on this branch**.
2. Wait for `.devcontainer/setup.sh` to finish (installs both frontend and
   backend deps, seeds the Payment Terms Master).
3. Fill in `backend/.env` with your Zoho OAuth credentials (Client ID/Secret,
   refresh token, workspace ID, org ID — see `backend/.env.example`).
4. Run `.devcontainer/start.sh` (or reload the window) to launch both
   servers. The **Ports** tab will show a forwarded, clickable URL for port
   `5173` — that's the live app.

**Option B — run locally on your own machine**

```
git clone <repo-url> && cd Central-Analytics
git checkout claude/scimplify-analytics-platform-nj168o
```

Backend:

```
cd backend
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env   # fill in Zoho OAuth credentials
.venv/bin/python -m scripts.seed_payment_terms
.venv/bin/uvicorn app.main:app --reload --port 8000
```

Frontend (separate terminal):

```
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The Vite dev server proxies `/api` to
`http://localhost:8000`.

## Tests

```
cd backend
.venv/bin/pytest
```
