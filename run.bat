@echo off
echo 🚀 Starting SecureBank Setup & Launch...

if not exist .env (
    echo 📄 .env file not found. Creating default .env file...
    (
        echo DATABASE_URL=postgresql+psycopg://securebank:securebank123@localhost:5432/securebank
        echo REDIS_URL=redis://localhost:6379
        echo JWT_SECRET_KEY=your_super_secret_key_change_in_production
        echo JWT_ALGORITHM=HS256
        echo ACCESS_TOKEN_EXPIRE_MINUTES=30
    ) > .env
    echo ✅ .env created.
)

echo 📦 Installing dependencies with uv...
call uv sync

echo 🐳 Starting Docker containers (PostgreSQL & Redis)...
call docker compose up -d postgres redis postgres_test

echo ⏳ Waiting for PostgreSQL to be ready...
timeout /t 3 /nobreak > NUL

echo 🗄️ Running Alembic database migrations...
call uv run alembic upgrade head

echo 🧹 Running Ruff lint check...
call uv run ruff check .

echo 🧪 Running Pytest suite...
call uv run pytest

echo 🌐 Launching SecureBank FastAPI Development Server...
echo 🔗 API Docs available at: http://127.0.0.1:8000/docs
call uv run fastapi dev src/securebank/main.py
