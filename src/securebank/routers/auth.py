from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from securebank.config import settings
from securebank.database import get_db
from securebank.dependencies import get_current_user
from securebank.models import User
from securebank.rate_limit import (
    check_login_rate_limit,
    clear_failed_logins,
    record_failed_login,
)
from securebank.schemas import TokenResponse, UserLogin, UserRegister, UserResponse
from securebank.secuirty import (
    create_access_token,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    user: UserRegister,
    db: Session = Depends(get_db),
):
    existing_user = db.scalar(select(User).where(User.email == user.email))

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        )

    hashed_password = hash_password(user.password)

    db_user = User(
        full_name=user.full_name,
        email=user.email,
        password_hash=hashed_password,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.post(
    "/login",
    response_model=TokenResponse,
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {
                "application/x-www-form-urlencoded": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "username": {"type": "string", "title": "Email / Username"},
                            "password": {
                                "type": "string",
                                "title": "Password",
                                "format": "password",
                            },
                        },
                        "required": ["username", "password"],
                    }
                },
                "application/json": {"schema": UserLogin.model_json_schema()},
            },
        }
    },
)
async def login_for_access_token(
    request: Request,
    db: Session = Depends(get_db),
):
    email, password = None, None
    content_type = request.headers.get("content-type", "")

    if "application/json" in content_type:
        try:
            body = await request.json()
            if isinstance(body, dict):
                email = body.get("email") or body.get("username")
                password = body.get("password")
        except Exception:
            pass
    else:
        try:
            form = await request.form()
            email = form.get("username") or form.get("email")
            password = form.get("password")
        except Exception:
            pass

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required",
        )

    check_login_rate_limit(email)

    user = db.scalar(select(User).where(User.email == email))

    if user is None or not verify_password(password, user.password_hash):
        record_failed_login(email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    clear_failed_logins(email)
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"user_id": user.id, "sub": str(user.id)},
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: User = Depends(get_current_user),
):
    return current_user
