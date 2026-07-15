#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."

cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
[ -f .env ] || cp .env.example .env
.venv/bin/python -m scripts.seed_payment_terms
cd ..

cd frontend
npm install
[ -f .env ] || cp .env.example .env
cd ..

echo ""
echo "Setup complete. Fill in backend/.env with your Zoho OAuth credentials, then reload the devcontainer (or run .devcontainer/start.sh) to launch both servers."
