from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from securebank.database import get_db
from securebank.dependencies import get_current_user, require_admin
from securebank.models import AuditLog, BankAccount, User
from securebank.schemas import AccountCreate, AccountResponse, AccountStatusUpdate
from securebank.utils import generate_account_number

router = APIRouter(
    prefix="/accounts",
    tags=["Accounts"],
)


@router.post(
    "",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_account(
    account_data: AccountCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    allowed_types = {
        "savings",
        "current",
    }

    account_type = account_data.account_type.lower()

    if account_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account type must be savings or current",
        )

    while True:
        account_number = generate_account_number()

        existing_account = db.scalar(
            select(BankAccount).where(BankAccount.account_number == account_number)
        )

        if not existing_account:
            break

    new_account = BankAccount(
        account_number=account_number,
        account_type=account_type,
        balance=0,
        user_id=current_user.id,
    )

    db.add(new_account)
    db.commit()
    db.refresh(new_account)

    return new_account


@router.get(
    "",
    response_model=list[AccountResponse],
)
def get_accounts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    accounts = db.scalars(
        select(BankAccount).where(BankAccount.user_id == current_user.id)
    ).all()

    return accounts


@router.get(
    "/{account_id}",
    response_model=AccountResponse,
)
def get_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    account = db.scalar(
        select(BankAccount).where(
            BankAccount.id == account_id,
            BankAccount.user_id == current_user.id,
        )
    )

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )

    return account


@router.patch(
    "/{account_id}/status",
    response_model=AccountResponse,
)
def update_account_status(
    account_id: int,
    status_data: AccountStatusUpdate,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    account = db.scalar(
        select(BankAccount).where(
            BankAccount.id == account_id,
        )
    )

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )

    account.is_active = status_data.is_active
    action = "unfreeze_account" if status_data.is_active else "freeze_account"

    audit_log = AuditLog(
        admin_user_id=admin_user.id,
        action=action,
        target_type="bank_account",
        target_id=account.id,
        details=(f"Account {account.account_number} status changed"),
    )
    db.add(audit_log)
    db.commit()
    db.refresh(account)

    return account
