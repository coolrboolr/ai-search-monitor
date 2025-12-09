#!/bin/bash
set -e

echo "=== KILLING OLD PROCESSES ==="
lsof -t -i:8000 | xargs kill -9 2>/dev/null || true
lsof -t -i:3000 | xargs kill -9 2>/dev/null || true

echo "=== REFRESHING DATA ==="
cd backend
source venv/bin/activate
export PYTHONPATH=$PYTHONPATH:.

# 1. Clear Data
python scripts/clear_data.py

# 2. Ingest Data (OpenAI enabled if in .env)
echo "Running ingestion pipeline..."
python -m src.ingestion.pipeline

echo "=== STARTING BACKEND ==="
# Run in background
nohup uvicorn src.api.main:app --reload --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend started (PID $BACKEND_PID). Logs: backend/backend.log"

echo "=== STARTING FRONTEND ==="
cd ../frontend
# interactive
npm run dev
