from fastapi import FastAPI

from .routers import accounts, admin, auth, transactions

app = FastAPI(
    title="SecureBank API",
    description="Banking Transaction Management System",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(accounts.router)
app.include_router(transactions.router)
app.include_router(admin.router)


@app.get("/")
def home():
    return {"message": "Welcome to SecureBank API"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
