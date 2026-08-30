# 🏦 SecureBank API

SecureBank is a high-performance, secure, and production-ready RESTful Banking API built with **FastAPI**, **SQLAlchemy (Async-compatible ORM)**, **PostgreSQL**, **Redis**, and **Alembic**. It features robust JWT-based authentication, Role-Based Access Control (RBAC), bank account management, financial transactions (deposits, withdrawals, transfers), audit logging, and Redis-backed rate limiting.

---

## 📋 Table of Contents

- [✨ Key Features](#-key-features)
- [🛠️ Tech Stack & Dependencies](#️-tech-stack--dependencies)
- [📁 Project Structure](#-project-structure)
- [🚀 Quick Start Guide (Local Setup)](#-quick-start-guide-local-setup)
- [🐳 Docker & Container Management](#-docker--container-management)
- [🗄️ Database Migrations (Alembic Guide)](#️-database-migrations-alembic-guide)
- [🧪 Testing Guide (Pytest)](#-testing-guide-pytest)
- [🧹 Code Quality & Linting (Ruff Guide)](#-code-quality--linting-ruff-guide)
- [🔄 CI/CD Pipeline (GitHub Actions)](#-cicd-pipeline-github-actions)
- [🚀 Render Deployment Guide](#-render-deployment-guide)
- [📚 Comprehensive Function & API Reference](#-comprehensive-function--api-reference)
  - [1. Data Models (`models.py`)](#1-data-models-modelspy)
  - [2. Pydantic Schemas (`schemas.py`)](#2-pydantic-schemas-schemaspy)
  - [3. Authentication & Security (`secuirty.py` & `auth.py`)](#3-authentication--security-secuitypy--authpy)
  - [4. Account Management (`accounts.py`)](#4-account-management-accountspy)
  - [5. Transactions (`transactions.py`)](#5-transactions-transactionspy)
  - [6. Admin & Audit Logs (`admin.py`)](#6-admin--audit-logs-adminpy)
  - [7. Dependencies & Middleware (`dependencies.py` & `rate_limit.py`)](#7-dependencies--middleware-dependenciespy--rate_limitpy)
  - [8. Utility Functions (`utils.py`)](#8-utility-functions-utilspy)
- [🛡️ Security Best Practices](#️-security-best-practices)

---

## ✨ Key Features

- 🔐 **JWT Authentication & RBAC**: Secure User Registration & Login with Password Hashing using `bcrypt` and role-based access (`customer` vs `admin`).
- 💳 **Banking Accounts**: Support for `savings` and `current` accounts with automatic, cryptographically secure account number generation (`SB...`).
- 💸 **Financial Transactions**: Atomic deposits, withdrawals, and inter-account transfers with optimistic/pessimistic row locking (`with_for_update`) to prevent race conditions and overdrafts.
- 🧊 **Account Status Controls**: Admin functionality to freeze (`is_active = False`) or unfreeze bank accounts with automatic enforcement across all financial endpoints (403 Forbidden on frozen accounts).
- 📜 **Audit Logging**: Immutable system audit trail recording administrative actions (account freeze/unfreeze) with admin user reference, target type, target ID, and timestamp.
- ⚡ **Redis Rate Limiting**: Protection against brute-force login attempts (max 5 failed attempts per 5-minute window).
- 🧪 **Complete Test Suite**: Unit and integration test coverage using `pytest`, `pytest-mock`, `httpx`, and Starlette `TestClient`.

---

## 🛠️ Tech Stack & Dependencies

| Tool / Library | Purpose |
| :--- | :--- |
| **FastAPI** | High-performance Python Web Framework |
| **Python 3.14** | Core Language |
| **UV** | Fast Python package installer and virtual environment manager |
| **SQLAlchemy 2.0** | SQL Toolkit & Object Relational Mapper (ORM) |
| **PostgreSQL 17** | Primary Relational Database |
| **Redis 7** | Cache & Rate Limiting Storage |
| **Alembic** | Database Schema Migration Engine |
| **PyJWT & Passlib / Bcrypt** | Security, Token Generation & Hashing |
| **Pytest** | Test Framework |
| **Ruff** | Extremely fast Python Linter and Code Formatter |
| **Docker & Docker Compose** | Multi-container Deployment Environment |
| **GitHub Actions** | Automated CI/CD Pipeline for Linting, Testing & Docker Build |

---

## 📁 Project Structure

```text
securebank/
├── alembic/                      # Alembic migration environment & revision scripts
│   ├── versions/                 # Database migration revision files
│   └── env.py                    # Alembic migration context configuration
├── src/
│   ├── securebank/               # Core application package
│   │   ├── routers/              # API Endpoint Handlers
│   │   │   ├── accounts.py       # Account creation, lookup & status update endpoints
│   │   │   ├── admin.py          # Admin audit log lookup endpoints
│   │   │   ├── auth.py           # User registration, login & profile endpoints
│   │   │   └── transactions.py   # Deposit, withdraw, transfer & history endpoints
│   │   ├── config.py             # Pydantic Settings configuration
│   │   ├── database.py           # SQLAlchemy engine & session factory setup
│   │   ├── dependencies.py       # FastAPI dependency injectors (get_db, require_admin, etc.)
│   │   ├── main.py               # FastAPI application entry point & router mounting
│   │   ├── models.py             # SQLAlchemy ORM Database Models (User, BankAccount, Transaction, AuditLog)
│   │   ├── rate_limit.py         # Redis-backed rate limiting logic
│   │   ├── redis_client.py       # Redis client connection instance
│   │   ├── schemas.py            # Pydantic Request & Response DTO Models
│   │   ├── secuirty.py           # Password hashing & JWT Token handling functions
│   │   └── utils.py              # Account number & transaction reference generators
│   └── tests/                    # Automated Test Suite
│       ├── conftest.py           # Test database setup, fixtures & mock overrides
│       ├── test_admin.py         # Tests for admin freeze/unfreeze and audit log routes
│       ├── test_auth.py          # Tests for authentication & token verification
│       ├── test_banking.py       # Tests for banking operations (accounts & transactions)
│       └── test_health.py        # Health check endpoint tests
├── .env                          # Environment variables configuration file
├── docker-compose.yml            # Docker Compose service declarations (Postgres, Redis, API)
├── Dockerfile                    # Container image build configuration
├── pyproject.toml                # Project metadata & dependency declarations
└── README.md                     # Documentation
```

---

## 🚀 Quick Start Guide (Local Setup)

### ⚡ Automatic One-Command Setup & Launch (Recommended)

Simply execute the script corresponding to your shell to automatically generate `.env`, sync dependencies, start Docker containers, apply database migrations, run Ruff & Pytest checks, and launch the development server:

```powershell
# Windows PowerShell
.\run.ps1
```

```cmd
# Windows Command Prompt
run.bat
```

```bash
# Linux / macOS / Git Bash
./run.sh
```

---

### 🛠️ Manual Step-by-Step Setup

#### 1. Prerequisites
- Python `>= 3.14`
- [`uv`](https://github.com/astral-sh/uv) installed (`pip install uv` or via installer)
- Docker Desktop or PostgreSQL & Redis installed locally

#### 2. Environment Setup
Create a `.env` file in the root directory:

```env
DATABASE_URL=postgresql+psycopg://securebank:securebank123@localhost:5432/securebank
REDIS_URL=redis://localhost:6379

JWT_SECRET_KEY=your_super_secret_key_change_in_production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Install Dependencies
Initialize virtual environment and sync dependencies using `uv`:

```bash
uv sync
```

### 4. Start Local Infrastructure (PostgreSQL & Redis)
Use Docker Compose to launch PostgreSQL and Redis containers:

```bash
docker compose up -d postgres redis
```

### 5. Apply Database Migrations
Run Alembic migrations to create database tables:

```bash
uv run alembic upgrade head
```

### 6. Run Development Server
Start the FastAPI development server:

```bash
uv run fastapi dev src/securebank/main.py
```

The interactive API documentation (Swagger UI) will be available at:
`http://127.0.0.1:8000/docs`

---

## 🌐 Connecting Neon Database (Serverless PostgreSQL)

Yes! You can seamlessly connect **Neon PostgreSQL** (Serverless PostgreSQL) to SecureBank without modifying any application code.

### 1. Obtain Connection String from Neon
From your [Neon Dashboard](https://console.neon.tech/), copy your database connection URI. It will look like this:
```text
postgres://alex:secretpassword@ep-sample-123.us-east-1.aws.neon.tech/neondb?sslmode=require
```

### 2. Format for SQLAlchemy & Psycopg 3
Change the scheme prefix from `postgres://` or `postgresql://` to `postgresql+psycopg://`:
```text
postgresql+psycopg://alex:secretpassword@ep-sample-123.us-east-1.aws.neon.tech/neondb?sslmode=require
```

### 3. Update Your `.env` File
Update the `DATABASE_URL` in `.env`:
```env
DATABASE_URL=postgresql+psycopg://alex:secretpassword@ep-sample-123.us-east-1.aws.neon.tech/neondb?sslmode=require
```

### 4. Run Migrations to Neon
Run Alembic migrations to build all database tables directly on Neon:
```bash
uv run alembic upgrade head
```

### 5. Start the Server
```bash
uv run fastapi dev src/securebank/main.py
```

---

## 🐳 Docker & Container Management

### Start All Services (PostgreSQL, Redis, API)

```bash
docker compose up -d --build
```

### Check Service Logs

```bash
# View all container logs
docker compose logs -f

# View API service logs only
docker compose logs -f api
```

### Stop Services

```bash
# Stop containers keeping volumes intact
docker compose stop

# Stop containers and remove networks
docker compose down

# Stop containers and remove volumes (reset database)
docker compose down -v
```

### Execute Commands Inside API Container

```bash
# Execute alembic migration inside API container
docker compose exec api uv run alembic upgrade head
```

---

## 🗄️ Database Migrations (Alembic Guide)

### Create a New Migration (Autogenerate Schema Changes)
After modifying ORM models in `src/securebank/models.py`, generate a new migration file:

```bash
uv run alembic revision --autogenerate -m "describe your changes here"
```

### Apply Migrations (Upgrade Database)
Upgrade the database schema to the latest revision (`head`):

```bash
uv run alembic upgrade head
```

### Rollback Migration (Downgrade Database)
Revert the last applied migration step:

```bash
uv run alembic downgrade -1
```

### View Migration History

```bash
uv run alembic history
```

---

## 🧪 Testing Guide (Pytest)

The project includes an isolated test suite running against a dedicated test database (`securebank_test` on port `5433`).

### 1. Ensure Test PostgreSQL Service is Running

```bash
docker compose up -d postgres_test
```

### 2. Run All Tests

```bash
uv run pytest -v
```

### 3. Run Specific Test File

```bash
# Run banking tests only
uv run pytest -v src/tests/test_banking.py

# Run admin tests only
uv run pytest -v src/tests/test_admin.py

# Run auth tests only
uv run pytest -v src/tests/test_auth.py
```

### 4. Run a Specific Test Function

```bash
uv run pytest -v -k "test_admin_can_freeze_account"
```

---

## 🧹 Code Quality & Linting (Ruff Guide)

Ruff is used for extremely fast Python linting and code formatting. The rules and formatting styles are configured in `pyproject.toml` under `[tool.ruff]`.

### 1. Check Code for Lint Errors

Run Ruff linter across the repository:

```bash
uv run ruff check .
```

### 2. Automatically Fix Lint Errors

Automatically fix safe linting and import ordering issues:

```bash
uv run ruff check --fix .
```

### 3. Check Code Formatting Compliance

Check if files comply with the formatting standard without modifying them:

```bash
uv run ruff format --check .
```

### 4. Format All Files

Apply standard formatting across all Python files:

```bash
uv run ruff format .
```

---

## 🔄 CI/CD Pipeline (GitHub Actions)

The repository includes a production-ready **GitHub Actions CI/CD workflow** configured in `.github/workflows/ci.yml`. It automatically triggers on every `push` and `pull_request` targeting the `main` or `master` branches.

### Pipeline Stages & Jobs:

1. **🧹 Code Quality & Linting (`lint`)**:
   - Uses `astral-sh/setup-uv` for fast dependency caching.
   - Runs `uv run ruff check .` to enforce linting rules.
   - Runs `uv run ruff format --check .` to verify code formatting compliance.

2. **🧪 Automated Test Suite (`test`)**:
   - Spins up **PostgreSQL 17** and **Redis 7** service containers in GitHub Actions runner environment.
   - Applies database migrations using `uv run alembic upgrade head`.
   - Executes the full Pytest suite with `uv run pytest -v`.

3. **🐳 Docker Container Build (`docker-build`)**:
   - Validates multi-stage Docker build using `docker/build-push-action`.
   - Guarantees container build readiness for production deployments.

---

## 🚀 Render Deployment Guide

SecureBank includes a pre-configured [`render.yaml`](file:///d:/securebank/render.yaml) Blueprint file to deploy the entire application stack (**FastAPI Web Service**, **PostgreSQL Database**, and **Redis Instance**) to [Render](https://render.com) with a single click.

### ⚡ 1-Click Deployment via Render Blueprint

1. Push your repository to **GitHub** or **GitLab**.
2. Log into the [Render Dashboard](https://dashboard.render.com/).
3. Click **New +** → Select **Blueprint**.
4. Connect your **SecureBank** GitHub repository.
5. Render will automatically detect [`render.yaml`](file:///d:/securebank/render.yaml) and provision:
   - Managed **PostgreSQL Database** (`securebank-db`)
   - Managed **Redis Instance** (`securebank-redis`)
   - **FastAPI Docker Web Service** (`securebank-api`)
   - Auto-generated strong `JWT_SECRET_KEY`
6. Click **Apply**.

Render will automatically build your Docker container, execute database migrations via `uv run alembic upgrade head` as a `preDeployCommand`, and issue a live SSL `https://...onrender.com` domain for your API and Swagger docs (`/docs`)..

---

## 📚 Comprehensive Function & API Reference

---

### 1. Data Models (`models.py`)

#### `User(Base)`
Represents system users (Customers and Administrators).
- `id` (`int`): Primary key.
- `full_name` (`str`): Full name of the user.
- `email` (`str`): Unique user email address (indexed).
- `password_hash` (`str`): Bcrypt password hash.
- `role` (`str`): User authorization level (`customer` or `admin`, default `customer`).
- `accounts`: ORM One-to-Many relationship to `BankAccount`.

#### `BankAccount(Base)`
Represents customer bank accounts.
- `id` (`int`): Primary key.
- `account_number` (`str`): Unique account number (`SB0000000000`).
- `account_type` (`str`): Account classification (`savings` or `current`).
- `is_active` (`bool`): Account freeze status (`True` = active, `False` = frozen).
- `daily_transfer_limit` (`Decimal`): Daily transfer cap (default `100,000.00`).
- `balance` (`Decimal`): Available account balance.
- `user_id` (`int`): Foreign key to `users.id`.
- `owner`: ORM Many-to-One relationship to `User`.

#### `Transaction(Base)`
Represents financial transactions performed on accounts.
- `id` (`int`): Primary key.
- `reference` (`str`): Unique transaction reference string (`TXN-XXXXXX`).
- `transaction_type` (`str`): Type of transaction (`deposit`, `withdraw`, `transfer_in`, `transfer_out`).
- `amount` (`Decimal`): Monetary transaction amount.
- `account_id` (`int`): Foreign key to `bank_accounts.id`.
- `status` (`str`): Transaction state (`completed`, `failed`).
- `description` (`str`): Human-readable note.
- `created_at` (`datetime`): Auto-generated timestamp.

#### `AuditLog(Base)`
Represents administrative audit entries.
- `id` (`int`): Primary key.
- `admin_user_id` (`int`): Foreign key to `users.id` (Admin user).
- `action` (`str`): Executed administrative action (e.g., `freeze_account`, `unfreeze_account`).
- `target_type` (`str`): Target entity classification (`bank_account`, `user`).
- `target_id` (`int`): Primary key ID of target entity.
- `details` (`str`): Additional context notes.
- `created_at` (`datetime`): Auto-generated timestamp.

---

### 2. Pydantic Schemas (`schemas.py`)

- `UserRegister`: Request schema for user registration (`full_name`, `email`, `password`).
- `UserLogin`: Request schema for authentication (`email`, `password`).
- `UserResponse`: Response schema for user details (`id`, `full_name`, `email`, `role`).
- `TokenResponse`: Response schema returning JWT bearer token (`access_token`, `token_type`).
- `AccountCreate`: Request schema for creating a bank account (`account_type`).
- `AccountResponse`: Response schema returning account details (`id`, `account_number`, `account_type`, `balance`, `is_active`, `daily_transfer_limit`).
- `AccountStatusUpdate`: Request schema for updating account freeze status (`is_active: bool`).
- `DepositRequest`: Request schema for account deposits (`account_id`, `amount > 0`).
- `WithdrawRequest`: Request schema for cash withdrawals (`account_id`, `amount > 0`).
- `TransferRequest`: Request schema for transfers (`source_account_id`, `destination_account_id`, `amount > 0`).
- `TransactionResponse`: Response schema for transaction records (`id`, `reference`, `transaction_type`, `amount`, `status`, `description`, `created_at`).
- `AuditLogResponse`: Response schema for audit log entries (`id`, `admin_user_id`, `action`, `target_type`, `target_id`, `details`, `created_at`).

---

### 3. Authentication & Security (`secuirty.py` & `auth.py`)

#### Security Utilities (`secuirty.py`)

##### `hash_password(password: str) -> str`
Hashes a plain-text password using `bcrypt.hashpw` and a randomly generated salt.

##### `verify_password(plain_password: str, hashed_password: str) -> bool`
Validates a plain-text password against a stored `bcrypt` hash using `bcrypt.checkpw`.

##### `create_access_token(data: dict, expires_delta: timedelta | None = None) -> str`
Generates a signed JWT access token containing claims (`sub`, `user_id`, `exp`) using `pyjwt` and configured secret key.

##### `decode_access_token(token: str) -> int`
Decodes and validates a JWT access token, returning the authenticated user's ID (`int`). Raises `401 Unauthorized` on invalid signature or expiration.

---

#### Auth Endpoints (`routers/auth.py`)

##### `POST /auth/register` (`register(user_data: UserRegister, db: Session)`)
Registers a new customer account. Checks for email uniqueness (`409 Conflict`), hashes the password, creates the `User` record, and returns `UserResponse` (`201 Created`).

##### `POST /auth/login` (`login(login_data: UserLogin, db: Session)`)
Authenticates user credentials. Enforces Redis rate limiting via `check_login_rate_limit`. On failed password match, invokes `record_failed_login` and returns `401 Unauthorized`. On success, clears failed attempt count via `clear_failed_logins` and returns a JWT `TokenResponse`.

##### `GET /auth/me` (`get_me(current_user: User = Depends(get_current_user))`)
Returns current authenticated user details (`UserResponse`).

---

### 4. Account Management (`accounts.py`)

##### `POST /accounts` (`create_account(account_data: AccountCreate, current_user: User, db: Session)`)
Creates a new bank account (`savings` or `current`) for the authenticated user. Generates a unique `account_number` (`SB...`) and initializes balance to `0.00` (`201 Created`).

##### `GET /accounts` (`get_accounts(current_user: User, db: Session)`)
Returns all bank accounts belonging to the current authenticated user (`200 OK`).

##### `GET /accounts/{account_id}` (`get_account(account_id: int, current_user: User, db: Session)`)
Returns account details by ID if owned by the current user. Returns `404 Not Found` if the account does not exist or belongs to another user (`200 OK`).

##### `PATCH /accounts/{account_id}/status` (`update_account_status(account_id: int, status_data: AccountStatusUpdate, admin_user: User = Depends(require_admin), db: Session)`)
**Admin Endpoint**: Updates account `is_active` state (`True` to unfreeze, `False` to freeze). Automatically inserts an entry into `audit_logs` table tracking the admin action (`200 OK`).

---

### 5. Transactions (`transactions.py`)

##### `POST /transactions/deposit` (`deposit_money(deposit_data: DepositRequest, current_user: User, db: Session)`)
Deposits funds into a user's account. Validates account ownership and checks account status. Returns `403 Forbidden` if account is inactive (`is_active = False`). Updates balance, creates a `deposit` transaction record, and commits (`201 Created`).

##### `POST /transactions/withdraw` (`withdraw_money(withdraw_data: WithdrawRequest, current_user: User, db: Session)`)
Withdraws funds from a user's account. Verifies account status (`403 Forbidden` if inactive) and sufficient balance (`400 Bad Request` if insufficient). Deducts balance, records a `withdraw` transaction, and commits (`201 Created`).

##### `POST /transactions/transfer` (`transfer_money(transfer_data: TransferRequest, current_user: User, db: Session)`)
Performs an atomic transfer between two bank accounts. Validates:
1. Source and destination accounts are distinct (`400 Bad Request`).
2. Source account ownership and `is_active` status (`403 Forbidden` if inactive).
3. Destination account existence.
4. Sufficient source account balance (`400 Bad Request`).

Executes balance changes atomically and creates dual transaction records (`transfer_out` for source, `transfer_in` for destination) inside a single DB transaction (`201 Created`).

##### `GET /transactions/account/{account_id}` (`get_transaction_history(account_id: int, current_user: User, db: Session)`)
Returns transaction history for the specified account in reverse chronological order (`200 OK`). Restricts access to account owner (`404 Not Found` if unowned).

---

### 6. Admin & Audit Logs (`admin.py`)

##### `GET /admin/audit-logs` (`get_audit_logs(admin_user: User = Depends(require_admin), db: Session)`)
**Admin Endpoint**: Returns system audit log entries (`AuditLogResponse`) in reverse chronological order. Protected by `require_admin` dependency (`403 Forbidden` for non-admin users).

---

### 7. Dependencies & Middleware (`dependencies.py` & `rate_limit.py`)

#### Dependencies (`dependencies.py`)

##### `get_db() -> Generator[Session]`
FastAPI dependency that yields a SQLAlchemy database session for the request lifecycle and closes it upon completion.

##### `get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User`
FastAPI dependency that extracts the OAuth2 Bearer token, decodes JWT user ID using `decode_access_token`, fetches the `User` from PostgreSQL, and injects it into endpoint handlers. Returns `401 Unauthorized` if invalid or missing.

##### `require_admin(current_user: User = Depends(get_current_user)) -> User`
FastAPI dependency that verifies `current_user.role == "admin"`. Raises `HTTPException(403 Forbidden, detail="Admin access required")` if the user is a standard customer.

---

#### Rate Limiter (`rate_limit.py`)

##### `check_login_rate_limit(email: str) -> None`
Checks Redis key `login_attempt:{email}`. If failed login attempts reach or exceed `5`, raises `HTTPException(429 Too Many Requests)`.

##### `record_failed_login(email: str) -> None`
Increments Redis key `login_attempt:{email}` by 1 and sets TTL expiration to 300 seconds (5 minutes) on first failure.

##### `clear_failed_logins(email: str) -> None`
Deletes Redis key `login_attempt:{email}` upon successful authentication.

---

### 8. Utility Functions (`utils.py`)

##### `generate_account_number() -> str`
Generates a random 10-digit account number formatted as `SB` + 10 digits (e.g., `SB0123456789`) using Python's cryptographically secure `secrets` module.

##### `generate_transaction_reference() -> str`
Generates a random 8-character hexadecimal reference string formatted as `TXN-` + uppercase hex (e.g., `TXN-A1B2C3D4`) using `secrets.token_hex(4)`.

---

## 🛡️ Security Best Practices

1. **Password Safety**: Passwords are hashed with `bcrypt` before storage; raw passwords are never logged or stored.
2. **Atomic Financial Transactions**: Row-level locking (`with_for_update()`) and explicit transaction rollbacks on exceptions prevent race conditions during balance operations.
3. **Immutability of Audit Logs**: Administrative changes generate immutable audit log records.
4. **Brute Force Defense**: Redis rate limiting locks login attempts per email after 5 consecutive failures for 5 minutes.
5. **Role-Based Authorization**: Standard customers cannot invoke admin endpoints or update account status.
