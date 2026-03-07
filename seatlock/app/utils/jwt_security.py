from datetime import datetime, timedelta, timezone
from app.config import jwt_settings
from jose import jwt
from jose import JWTError
from fastapi import HTTPException, status
from uuid_utils import uuid7


def create_jwt_token(data: dict) -> str:
    data_copy = data.copy()
    data_copy["exp"] = datetime.now(timezone.utc) + timedelta(
        minutes=jwt_settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    data_copy["jti"] = str(uuid7())

    try:
        res = jwt.encode(
            data_copy, jwt_settings.JWT_SECRET_KEY, algorithm=jwt_settings.JWT_ALGORITHM
        )
        return res
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Some issue occurred please try to login again",
        )


def decode_jwt(jwt_token: str) -> dict:
    try:
        return jwt.decode(
            jwt_token,
            jwt_settings.JWT_SECRET_KEY,
            algorithms=[jwt_settings.JWT_ALGORITHM],
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
