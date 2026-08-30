from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    full_name: str = Field(
        min_length=2,
        max_length=100,
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str

    model_config = {"from_attributes": True}


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class AccountCreate(BaseModel):
    account_type: str = Field(
        min_length=3,
        max_length=20,
    )


class AccountResponse(BaseModel):
    id: int
    account_number: str
    account_type: str
    balance: Decimal
    user_id: int
    is_active: bool
    daily_transfer_limit: Decimal

    model_config = {"from_attributes": True}


class DepositRequest(BaseModel):
    account_id: int
    amount: Decimal = Field(gt=0)


class TransactionResponse(BaseModel):
    id: int
    reference: str
    transaction_type: str
    amount: Decimal
    status: str
    description: str | None
    account_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class AccountStatusUpdate(BaseModel):
    is_active: bool


class WithdrawRequest(BaseModel):
    account_id: int
    amount: Decimal = Field(gt=0)


class TransferRequest(BaseModel):
    source_account_id: int
    destination_account_id: int
    amount: Decimal = Field(gt=0)


class AuditLogResponse(BaseModel):
    id: int
    admin_user_id: int
    action: str
    target_type: str
    target_id: int
    details: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
