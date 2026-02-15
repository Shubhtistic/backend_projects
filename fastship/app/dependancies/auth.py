from typing import Annotated
from fastapi import Depends, HTTPException, status
from app.dependancies.db_dependancy import DbSessionDep
from app.security.jwt import decode_jwt
from sqlalchemy.future import select
from app.database.db_models import Seller

from fastapi.security import OAuth2PasswordBearer

# OAUTH2PasswordBearer -> inbuilt fastapi to check if header contains the jwt token if not the 401 error


oauth2 = OAuth2PasswordBearer(tokenUrl="auth/login")
# tokenUrl="login"
# This is for the Docs (/docs page).
# It tells Swagger UI: "If the user isn't logged in, send them to the /login endpoint to get a token."


async def current_user(db: DbSessionDep, token: str = Depends(oauth2)):

    res = decode_jwt(token)
    email = res.get("sub")

    qry = select(Seller).where(Seller.email == email)
    ans = (await db.execute(qry)).scalar_one_or_none()
    if ans is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="This user Does not exist"
        )
    return ans


CurrentUserDep = Annotated[Seller, Depends(current_user)]
