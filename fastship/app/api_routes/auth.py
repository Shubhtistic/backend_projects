from datetime import datetime, timezone
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, status, HTTPException, Body

from app.dependancies.db_dependancy import DbSessionDep
from app.dependancies.auth import CurrentUserDep
from app.schemas.user_auth import CreateUser, ReadUser
from sqlalchemy.future import select
from app.database.db_models import Seller, RefreshToken
from app.security.utils import verify_hash_password, generate_hash
from app.security.jwt import create_access_token
from app.security.refresh_token import (
    create_refresh_token,
    get_refresh_token_expiry,
    hash_refresh_token,
)
from app.schemas.user_auth import RefreshRequest, LogoutRequest


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
    user = (await db.execute(query)).scalar_one_or_none()

    if user is None or not verify_hash_password(
        form_data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Either email or password is incorrect",
        )

    # create a jwt access tokn
    access_token = create_access_token(subject=user.email)

    raw_refresh_token = create_refresh_token()

    hashed_refresh_token = hash_refresh_token(raw_refresh_token)

    refresh_expiry = get_refresh_token_expiry()

    # add refresh token in db
    refresh_token_obj = RefreshToken(
        user_id=user.id,
        token_hash=hashed_refresh_token,
        expires_at=refresh_expiry,
    )

    db.add(refresh_token_obj)
    await db.commit()
    await db.refresh(refresh_token_obj)

    return {
        "access_token": access_token,
        "refresh_token": raw_refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh")
async def refresh_token(
    db: DbSessionDep,
    request: RefreshRequest,
):
    hashed_token = hash_refresh_token(request.refresh_token)

    query = select(RefreshToken).where(RefreshToken.token_hash == hashed_token)
    token_obj = (await db.execute(query)).scalar_one_or_none()

    if token_obj is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    if token_obj.revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token revoked",
        )

    if token_obj.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
        )

    user_query = select(Seller).where(Seller.id == token_obj.user_id)
    user = (await db.execute(user_query)).scalar_one_or_none()

    # what if user is None
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # Rotate: delete old refresh token
    await db.delete(token_obj)

    # Create new tokens

    new_access_token = create_access_token(subject=user.email)
    raw_refresh_token = create_refresh_token()
    hashed_refresh_token = hash_refresh_token(raw_refresh_token)
    refresh_expiry = get_refresh_token_expiry()

    new_refresh_obj = RefreshToken(
        user_id=user.id,
        token_hash=hashed_refresh_token,
        expires_at=refresh_expiry,
    )

    db.add(new_refresh_obj)
    await db.commit()

    return {
        "access_token": new_access_token,
        "refresh_token": raw_refresh_token,
        "token_type": "bearer",
    }


@router.post("/logout")
async def logout(
    db: DbSessionDep,
    request: LogoutRequest,
):
    hashed_token = hash_refresh_token(request.refresh_token)

    query = select(RefreshToken).where(RefreshToken.token_hash == hashed_token)
    token_obj = (await db.execute(query)).scalar_one_or_none()

    if token_obj is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    await db.delete(token_obj)
    await db.commit()

    return {"message": "Logged out successfully"}


@router.get("/me", response_model=ReadUser)
async def current_user(user: CurrentUserDep):
    return user
