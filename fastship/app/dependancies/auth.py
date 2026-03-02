from typing import Annotated
from fastapi import Depends, HTTPException, status
from app.dependancies.db_dependancy import DbSessionDep
from app.security.jwt import decode_jwt
from sqlalchemy.future import select
from app.database.db_models import Account
from app.schemas.enums import UserRole
from fastapi.security import OAuth2PasswordBearer


oauth2 = OAuth2PasswordBearer(tokenUrl="auth/login")


class AuthUser:
    def __init__(self, account: Account, roles: list[UserRole]):
        self.account = account
        self.roles = roles


async def current_user(db: DbSessionDep, token: str = Depends(oauth2)):

    payload = decode_jwt(token)

    account_id = payload.get("sub")
    roles = payload.get("roles", [])

    if account_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    # single DB hit
    qry = select(Account).where(Account.id == account_id)
    account = (await db.execute(qry)).scalar_one_or_none()

    if account is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User does not exist",
        )

    return AuthUser(account=account, roles=roles)


CurrentUserDep = Annotated[AuthUser, Depends(current_user)]
