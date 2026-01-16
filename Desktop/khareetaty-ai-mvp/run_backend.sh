#!/bin/bash
# Khareetaty AI - Backend Startup Script

cd "$(dirname "$0")"

export PYTHONPATH="${PWD}:${PYTHONPATH}"

echo "🚀 Starting Khareetaty AI Backend..."
echo "📍 Working directory: ${PWD}"
echo "🐍 Python path: ${PYTHONPATH}"
echo ""

python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
