from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
import jwt
from fastapi import HTTPException, status

from .config import settings


def hash_password(password: str) -> str:
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)
    to_encode.update({"exp": expire})

    # Ensure both sub and user_id claims exist for compatibility
    if "user_id" in to_encode and "sub" not in to_encode:
        to_encode["sub"] = str(to_encode["user_id"])
    elif "sub" in to_encode and "user_id" not in to_encode:
        try:
            to_encode["user_id"] = int(to_encode["sub"])
        except ValueError:
            pass

    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def decode_access_token(token: str) -> int:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        raw_id = payload.get("sub") or payload.get("user_id")
        if raw_id is None:
            raise credentials_exception
        return int(raw_id)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, ValueError) as err:
        raise credentials_exception from err
