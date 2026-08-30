from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from securebank.database import get_db
from securebank.dependencies import get_current_user
from securebank.models import BankAccount, Transaction, User
from securebank.schemas import (
    DepositRequest,
    TransactionResponse,
    TransferRequest,
    WithdrawRequest,
)
from securebank.utils import generate_transaction_reference

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"],
)


@router.post(
    "/deposit",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def deposit_money(
    deposit_data: DepositRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        account = db.scalar(
            select(BankAccount)
            .where(
                BankAccount.id == deposit_data.account_id,
                BankAccount.user_id == current_user.id,
            )
            .with_for_update()
        )

        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found",
            )

        if not account.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is not active",
            )

        account.balance += deposit_data.amount

        transaction = Transaction(
            reference=generate_transaction_reference(),
            transaction_type="deposit",
            amount=deposit_data.amount,
            status="completed",
            description="Deposit",
            account_id=account.id,
        )

        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        return transaction

    except HTTPException:
        db.rollback()
        raise

    except Exception as err:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Deposit failed",
        ) from err


@router.post(
    "/withdraw",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def withdraw_money(
    withdraw_data: WithdrawRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        account = db.scalar(
            select(BankAccount)
            .where(
                BankAccount.id == withdraw_data.account_id,
                BankAccount.user_id == current_user.id,
            )
            .with_for_update()
        )

        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found",
            )

        if not account.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is not active",
            )

        if account.balance < withdraw_data.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient balance",
            )

        account.balance -= withdraw_data.amount

        transaction = Transaction(
            reference=generate_transaction_reference(),
            transaction_type="withdraw",
            amount=withdraw_data.amount,
            status="completed",
            description="Cash withdrawal",
            account_id=account.id,
        )

        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        return transaction

    except HTTPException:
        db.rollback()
        raise

    except Exception as err:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Withdrawal failed",
        ) from err


@router.post(
    "/transfer",
    status_code=status.HTTP_201_CREATED,
)
def transfer_money(
    transfer_data: TransferRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if transfer_data.source_account_id == transfer_data.destination_account_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Source and destination accounts cannot be the same",
        )

    try:
        source_account = db.scalar(
            select(BankAccount)
            .where(
                BankAccount.id == transfer_data.source_account_id,
                BankAccount.user_id == current_user.id,
            )
            .with_for_update()
        )

        if not source_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source account not found",
            )

        if not source_account.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Source account is not active",
            )

        destination_account = db.scalar(
            select(BankAccount)
            .where(BankAccount.id == transfer_data.destination_account_id)
            .with_for_update()
        )

        if not destination_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Destination account not found",
            )

        if source_account.balance < transfer_data.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient balance",
            )

        source_account.balance -= transfer_data.amount
        destination_account.balance += transfer_data.amount

        debit_transaction = Transaction(
            transaction_type="transfer_out",
            reference=generate_transaction_reference(),
            amount=transfer_data.amount,
            account_id=source_account.id,
            status="completed",
            description="Transfer",
        )

        credit_transaction = Transaction(
            transaction_type="transfer_in",
            reference=generate_transaction_reference(),
            amount=transfer_data.amount,
            account_id=destination_account.id,
            status="completed",
            description="Transfer",
        )

        db.add_all(
            [
                debit_transaction,
                credit_transaction,
            ]
        )

        db.commit()

        return {
            "message": "Transfer successful",
            "amount": transfer_data.amount,
            "source_account_id": source_account.id,
            "destination_account_id": destination_account.id,
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception as err:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transfer failed",
        ) from err


@router.get(
    "/account/{account_id}",
    response_model=list[TransactionResponse],
    status_code=status.HTTP_200_OK,
)
def get_transaction_history(
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

    transactions = db.scalars(
        select(Transaction)
        .where(Transaction.account_id == account.id)
        .order_by(Transaction.created_at.desc())
    ).all()

    return transactions
