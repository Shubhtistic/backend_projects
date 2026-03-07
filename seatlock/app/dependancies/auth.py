from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.dependancies.db_dependancy import DbSessionDep
from app.utils.jwt_security import decode_jwt
from app.database.db_models import Users
from sqlalchemy import select
from typing import Annotated
from app.dependancies.redis_blacklist import check_jti_blacklist

oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login")


# verfied, we verified the jwt token against our secret key and the token is valid
# so we know that this user exists in our database, but we dont know if he/she is banned or not
# use in read only endpoints like getiing events or showing prices or availibilty
async def get_verified_user(token: str = Depends(oauth2)):
    payload = decode_jwt(token)  # raises 401 internally if invalid/expired
    user_id = payload.get("sub")
    jti = payload.get("jti")

    if user_id is None or jti is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid jwt token, log in again",
        )

    # lets check if jti is blacklisted or not
    if await check_jti_blacklist(jti=jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid jwt token, log in again",
        )

    return user_id


# active user -> strongest check , jwt needs to be valid and and user must not be banned in database
# use in important routes booking, cancel booking, etc
async def get_active_user(db: DbSessionDep, token: str = Depends(oauth2)):
    payload = decode_jwt(token)  # raises 401 internally if invalid/expired
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid jwt token, please login again",
        )

    qry = select(Users.is_active).where(Users.user_id == user_id)
    res = (await db.execute(qry)).one_or_none()  # Row object or None
    if res is None or not res.is_active:  # None = deleted, False = banned
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials, login again",
        )
    return user_id


# Verified = JWT only,  ActiveUser = JWT + DB
#   async def get_events(user_id: CurrentUser)        → anyone with valid JWT
#   async def create_booking(user_id: CurrentActiveUser) → must be active in DB
CurrentUser = Annotated[str, Depends(get_verified_user)]
CurrentActiveUser = Annotated[str, Depends(get_active_user)]
