from datetime import timedelta, datetime, timezone
import hashlib
from uuid import uuid4


def create_refresh_token():
    return str(uuid4())


def get_refresh_token_expiry(num_days: int = 7) -> timedelta:
    return datetime.now(timezone.utc) + timedelta(days=num_days)


def get_hashed_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
    # hashlib expects a bytes and not python string, encode token
    # encode() -> defaults to utf 8
