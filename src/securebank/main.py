from fastapi import FastAPI
from scalar_fastapi import add_scalar_reference

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

add_scalar_reference(app)


@app.get("/")
def home():
    return {
        "message": "Welcome to SecureBank API",
        "docs": "/scalar",
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}
