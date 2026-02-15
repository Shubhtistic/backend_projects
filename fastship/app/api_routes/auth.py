from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends
from fastapi import status, HTTPException

from app.dependancies.db_dependancy import DbSessionDep
from app.dependancies.auth import CurrentUserDep
from app.schemas.user_auth import CreateUser, ReadUser
from sqlalchemy.future import select
from app.database.db_models import Seller
from app.security.utils import verify_hash_password, generate_hash
from app.security.jwt import create_token

from app.config import jwt_settings

from app.dependancies.auth import CurrentUserDep

router = APIRouter(prefix="/auth")


@router.post("/register", response_model=ReadUser)
async def register_user(user: CreateUser, db: DbSessionDep):
    ## check if email already exists

    normalized_email = user.email.lower()
    qry = select(Seller).where(Seller.email == normalized_email)

    res = await db.execute(qry)
    existing_seller = res.scalar_one_or_none()
    if existing_seller is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="the user already exists"
        )

    hashed_password = generate_hash(user.password)

    # new_user=user.model_dump()
    # ## convert pydantic schema to db

    ## make email lowercase to avoid any issue
    new_seller = Seller(
        name=user.name, email=normalized_email, hashed_password=hashed_password
    )
    db.add(new_seller)
    await db.commit()
    await db.refresh(new_seller)

    return new_seller


@router.post("/login")
async def login_user(
    db: DbSessionDep,
    form_data: OAuth2PasswordRequestForm = Depends(),
):

    normalized_email = form_data.username.lower()
    query = select(Seller).where(Seller.email == normalized_email)
    res = (await db.execute(query)).scalar_one_or_none()
    if (res is None) or not verify_hash_password(
        form_data.password, hashed_password=res.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Either email or Password is Wrong",
        )
    data = {
        "sub": res.email,
        "exp": datetime.now(timezone.utc)
        + timedelta(minutes=jwt_settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    token = create_token(data=data)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=ReadUser)
async def current_user(user: CurrentUserDep):
    return user
