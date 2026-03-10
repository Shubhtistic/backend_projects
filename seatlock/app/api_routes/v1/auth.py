from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from app.database.db_models import Users, RefreshToken
from app.dependancies.db_dependancy import DbSessionDep
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, join, delete
from app.dependancies.redis_blacklist import add_jti_to_blacklist
from app.schemas.user_auth import CreateUser, LogoutRequest, RefreshTokenReq, ReturnUser
from app.utils.password import hash_password, verify_hashed_password
from app.utils.phone_number import verify_mob_num
from app.utils.jwt_security import create_jwt_token, decode_jwt
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
    return user_data


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


@router.post("/refresh")
async def refresh(db: DbSessionDep, refresh_token: RefreshTokenReq):
    """Once the jwt is expired, we redirect user internally to this endpoint
    takes the users refresh token, validates it against the db and assigns a new refresh token and jwt token
    """
    hashed_rt = get_hashed_refresh_token(refresh_token.refresh_token)
    qry = (
        select(Users.is_active, RefreshToken.expiry_date, Users.user_id)
        .join(Users, RefreshToken.user_id == Users.user_id)
        .where(RefreshToken.hashed_token == hashed_rt)
    )
    # select is_active from Users
    # join RefreshToken on RefreshToken.user_id = Users.user_id
    # where RefreshToken.hashed_value==hashed_rt
    res = (await db.execute(qry)).one_or_none()

    # if no records -> None i.e Falsy Value
    # if user banned -> False
    # if record found -> True
    # the statement ->  False is None == False
    if res is None or res.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized user Or Expired Refresh Token Login Again",
        )
    if res.expiry_date < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized user Or Expired Refresh Token Login Again",
        )

    # if not -> refresh token was in db and user was valid and not banned
    # lets first delete the old token
    del_qry = delete(RefreshToken).where(RefreshToken.hashed_token == hashed_rt)
    await db.execute(del_qry)

    # get new tokens
    raw_refresh_token = create_refresh_token()
    hashed_refresh_token = get_hashed_refresh_token(raw_refresh_token)
    refresh_token_expiry = get_refresh_token_expiry()

    # jwt
    jwt_token = create_jwt_token({"sub": str(res.user_id)})

    new_refresh_token = RefreshToken(
        user_id=res.user_id,
        expiry_date=refresh_token_expiry,
        hashed_token=hashed_refresh_token,
    )
    db.add(new_refresh_token)
    await db.commit()  # commited delete + new insert

    # await db.refresh(new_refresh_token) .. not needed we dont have to return anything apart from raw refresh token

    return {
        "access_token": jwt_token,
        "refresh_token": raw_refresh_token,
        "token_type": "bearer",
    }


@router.post("/logout")
async def logout(db: DbSessionDep, tokens: LogoutRequest):
    refresh_token = tokens.refresh_token
    jwt_access_token = tokens.access_token

    # lets first see is jwt even valid before hiting db
    payload = decode_jwt(
        jwt_access_token
    )  # is any error 401 is raised directly by decode_jwt function
    exp = payload.get("exp")  # exp in unix timestamp
    jti = payload.get("jti")

    await add_jti_to_blacklist(jti, exp)
    # just use a single db hit -> directly query with given token
    # if its exists -> gets deleted
    # if does not exist -> no operation
    hashed_refesh_token = get_hashed_refresh_token(refresh_token)
    del_qry = delete(RefreshToken).where(
        RefreshToken.hashed_token == hashed_refesh_token
    )
    await db.execute(del_qry)
    await db.commit()

    return {"message": "Log Out Successful"}
