from fastapi import HTTPException, status

from securebank.redis_client import redis_client


MAX_LOGIN_ATTEMPTS = 5
LOGIN_WINDOW_SECONDS = 300


def check_login_rate_limit(email: str) -> None:
    key = f"login_attempt:{email}"

    attempts = redis_client.get(key)

    if attempts and int(attempts) >= MAX_LOGIN_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Try again later.",
        )


def record_failed_login(email: str) -> None:
    key = f"login_attempt:{email}"

    attempts = redis_client.incr(key)

    if attempts == 1:
        redis_client.expire(
            key,
            LOGIN_WINDOW_SECONDS,
        )


def clear_failed_logins(email: str) -> None:
    key = f"login_attempt:{email}"

    redis_client.delete(key)