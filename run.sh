#!/usr/bin/env bash
set -e

echo "🚀 Starting SecureBank Setup & Launch..."

# 1. Check/Create .env file
if [ ! -f .env ]; then
    echo "📄 .env file not found. Creating default .env file..."
    cat << 'EOF' > .env
DATABASE_URL=postgresql+psycopg://securebank:securebank123@localhost:5432/securebank
REDIS_URL=redis://localhost:6379

JWT_SECRET_KEY=your_super_secret_key_change_in_production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
EOF
    echo "✅ .env created."
fi

# 2. Sync dependencies using uv
echo "📦 Installing dependencies with uv..."
uv sync

# 3. Start Docker Compose services
echo "🐳 Starting Docker containers (PostgreSQL & Redis)..."
docker compose up -d postgres redis postgres_test

# 4. Wait for database readiness
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 3

# 5. Run Database Migrations
echo "🗄️ Running Alembic database migrations..."
uv run alembic upgrade head

# 6. Run Ruff linting & Pytest test suite
echo "🧹 Running Ruff lint check..."
uv run ruff check .

echo "🧪 Running Pytest suite..."
uv run pytest

# 7. Start Dev Server
echo "🌐 Launching SecureBank FastAPI Development Server..."
echo "🔗 API Docs available at: http://127.0.0.1:8000/docs"
uv run fastapi dev src/securebank/main.py
