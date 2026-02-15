from fastapi import HTTPException, status
from jose import jwt, JWTError
from app.config import jwt_settings


def create_token(data: dict):

    to_encode = data.copy()
    encoded_jwt = jwt.encode(
        to_encode, jwt_settings.JWT_SECRET_KEY, algorithm=jwt_settings.JWT_ALGORITHM
    )

    return encoded_jwt


def decode_jwt(token) -> dict:

    try:
        payload = jwt.decode(
            token, jwt_settings.JWT_SECRET_KEY, algorithms=[jwt_settings.JWT_ALGORITHM]
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

