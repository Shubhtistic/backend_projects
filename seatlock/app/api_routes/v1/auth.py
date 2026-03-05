from fastapi import APIRouter, Depends, HTTPException, status
from app.database.db_models import Users, RefreshToken
from app.dependancies.db_dependancy import DbSessionDep
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from app.schemas.user import CreateUser, ReturnUser
from app.utils.password import hash_password, verify_hashed_password
from app.utils.phone_number import verify_mob_num
from app.utils.jwt_security import create_jwt_token
from app.utils.refresh_token import (
    create_refresh_token,
    get_hashed_refresh_token,
    get_refresh_token_expiry,
)

router = APIRouter(prefix="/auth")


@router.post("/register", response_model=ReturnUser)
async def register_user(user_data: CreateUser, db: DbSessionDep):
    normalized_email = user_data.email.lower()
    qry = select(1).where(Users.email == normalized_email)
    # existence check query just return a simple integer '1'
    res = (await db.execute(qry)).scalar_one_or_none()

    if res is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User Already exists or is banned",
        )
    hashed_password = hash_password(user_data.password)
    mob_no = verify_mob_num(user_data.mobile_no)

    new_user = Users(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=normalized_email,
        hashed_password=hashed_password,
        mobile_no=mob_no,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.post("/login")
async def login_user(
    db: DbSessionDep, form_data: OAuth2PasswordRequestForm = Depends()
):
    normalized_email = form_data.username.lower()
    qry = select(Users.hashed_password, Users.user_id).where(
        Users.email == normalized_email
    )
    res = (await db.execute(qry)).one_or_none()

    if (res is None) or (
        not verify_hashed_password(form_data.password, res.hashed_password)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Either username or password is incorrect",
        )
    ## valid user
    jwt_token = create_jwt_token(data={"sub": str(res.user_id)})

    raw_refresh_token = create_refresh_token()
    hashed_refresh_token = get_hashed_refresh_token(raw_refresh_token)
    refresh_token_exp = get_refresh_token_expiry()

    new_refresh_token = RefreshToken(
        user_id=res.user_id,
        expiry_date=refresh_token_exp,
        hashed_token=hashed_refresh_token,
    )
    db.add(new_refresh_token)
    await db.commit()
    await db.refresh(new_refresh_token)

    return {
        "access_token": jwt_token,
        "refresh_token": raw_refresh_token,
        "token_type": "bearer",
    }
