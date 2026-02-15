import uuid
from datetime import datetime, timedelta, timezone
import hashlib


def create_refresh_token():
    """
    Generates a secure random refresh token string.
    This raw value is sent to client.
    """
    return str(uuid.uuid4())


def get_refresh_token_expiry(days: int = 7):
    """
    return exp date for each refresh token
    """
    return datetime.now(timezone.utc) + timedelta(days=days)


def hash_refresh_token(token: str) -> str:
    """
    hash the refresh token and store it in Db
    """
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
