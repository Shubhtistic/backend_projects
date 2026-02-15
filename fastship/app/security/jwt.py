from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from jose import jwt, JWTError
from app.config import jwt_settings


def create_access_token(subject: str) -> str:
    """
    genearates a short duration jwt token
    """

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=jwt_settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": subject,
        "exp": expire,
    }

    encoded_jwt = jwt.encode(
        payload,
        jwt_settings.JWT_SECRET_KEY,
        algorithm=jwt_settings.JWT_ALGORITHM,
    )

    return encoded_jwt


def decode_jwt(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            jwt_settings.JWT_SECRET_KEY,
            algorithms=[jwt_settings.JWT_ALGORITHM],
        )

        if payload.get("sub") is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    return payload
