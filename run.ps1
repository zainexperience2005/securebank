# PowerShell script to set up and run SecureBank project
$ErrorActionPreference = "Stop"

Write-Host "Starting SecureBank Setup and Launch..." -ForegroundColor Cyan

# 1. Check/Create .env file
if (-not (Test-Path ".env")) {
    Write-Host ".env file not found. Creating default .env file..." -ForegroundColor Yellow
    @'
DATABASE_URL=postgresql+psycopg://securebank:securebank123@localhost:5432/securebank
REDIS_URL=redis://localhost:6379

JWT_SECRET_KEY=your_super_secret_key_change_in_production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
'@ | Out-File -FilePath ".env" -Encoding utf8
    Write-Host ".env created." -ForegroundColor Green
}

# 2. Sync dependencies using uv
Write-Host "Installing dependencies with uv..." -ForegroundColor Cyan
uv sync

# 3. Start Docker Compose services
Write-Host "Starting Docker containers (PostgreSQL and Redis)..." -ForegroundColor Cyan
docker compose up -d postgres redis postgres_test

# 4. Wait for database readiness
Write-Host "Waiting for PostgreSQL to be ready..." -ForegroundColor Cyan
Start-Sleep -Seconds 3

# 5. Run Database Migrations
Write-Host "Running Alembic database migrations..." -ForegroundColor Cyan
uv run alembic upgrade head

# 6. Run Ruff linting and Pytest test suite
Write-Host "Running Ruff lint check..." -ForegroundColor Cyan
uv run ruff check .

Write-Host "Running Pytest suite..." -ForegroundColor Cyan
uv run pytest

# 7. Start Dev Server
Write-Host "Launching SecureBank FastAPI Development Server..." -ForegroundColor Green
Write-Host "API Docs available at: http://127.0.0.1:8000/docs" -ForegroundColor Yellow
uv run fastapi dev src/securebank/main.py
