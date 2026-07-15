#!/usr/bin/env bash
cd "$(dirname "$0")/.."

pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "vite --port 5173" 2>/dev/null || true

(cd backend && nohup .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &)
(cd frontend && nohup npm run dev -- --host 0.0.0.0 --port 5173 > /tmp/frontend.log 2>&1 &)

sleep 2
echo "Backend running on port 8000 (log: /tmp/backend.log)"
echo "Frontend running on port 5173 (log: /tmp/frontend.log) — check the Ports tab for the forwarded preview URL"
