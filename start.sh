#!/bin/sh
set -e

echo "🗄️ Running database migrations with Alembic..."
/app/.venv/bin/alembic upgrade head

echo "🌐 Starting Uvicorn server..."
exec /app/.venv/bin/uvicorn securebank.main:app --host 0.0.0.0 --port 8000
