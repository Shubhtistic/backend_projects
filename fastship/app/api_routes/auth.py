from datetime import datetime, timezone
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, status, HTTPException, Body

from app.dependancies.db_dependancy import DbSessionDep
from app.dependancies.auth import CurrentUserDep
from app.schemas.user_auth import CreateUser, ReadUser
from sqlalchemy.future import select
from sqlalchemy import join, delete
from app.database.db_models import Account, Seller, RefreshToken, DeliveryPartner
from app.security.utils import verify_hash_password, generate_hash
from app.security.jwt import create_access_token
from app.security.refresh_token import (
    create_refresh_token,
    get_refresh_token_expiry,
    hash_refresh_token,
)
from app.schemas.user_auth import RefreshRequest, LogoutRequest
from app.schemas.enums import UserRole

router = APIRouter(prefix="/auth")


@router.post("/register", response_model=ReadUser)
async def register_user(user: CreateUser, db: DbSessionDep):
    ## check if email already exists

    normalized_email = user.email.lower()
    qry = select(Account).where(Account.email == normalized_email)
    existing_seller = (await db.execute(qry)).scalar_one_or_none()
    if existing_seller is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="the user already exists"
        )

    hashed_password = generate_hash(user.password)

    # new_user=user.model_dump()
    # ## convert pydantic schema to db

    ## make email lowercase to avoid any issue
    new_acc = Account(
        name=user.name, email=normalized_email, hashed_password=hashed_password
    )

    db.add(new_acc)
    await db.commit()
    await db.refresh(new_acc)

    return new_acc


@router.post("/login")
async def login_user(
    db: DbSessionDep,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    normalized_email = form_data.username.lower()

    query = (
        select(
            Account.id,
            Account.email,
            Account.hashed_password,
            Seller.seller_id,
            DeliveryPartner.delivery_partner_id,
        )
        .outerjoin(Seller, Account.id == Seller.seller_id)
        .outerjoin(DeliveryPartner, Account.id == DeliveryPartner.delivery_partner_id)
        .where(Account.email == normalized_email)
    )

    user = (await db.execute(query)).first()
    # what first does -> if no rows then returns None
    # if rows found then a orm row object

    if user is None or not verify_hash_password(
        form_data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Either email or password is incorrect",
        )

    if (user.seller_id is None) and (user.delivery_partner_id is None):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User has no role"
        )
    # creates roles list
    roles: list[str] = []  # become a json array in response

    if user.seller_id is not None:
        roles.append(UserRole.SELLER)

    if user.delivery_partner_id is not None:
        roles.append(UserRole.DELIVERY_PARTNER)

    # create a jwt access tokn
    access_token = create_access_token(subject=str(user.id), roles=roles)

    raw_refresh_token = create_refresh_token()

    hashed_refresh_token = hash_refresh_token(raw_refresh_token)

    refresh_expiry = get_refresh_token_expiry()

    # add refresh token in db
    refresh_token_obj = RefreshToken(
        account_id=user.id,
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

    # lets get the whole 'refreshtoken' orm object as it has less columns and will make it easy to delete also
    query = select(RefreshToken).where(hashed_token == RefreshToken.token_hash)
    ## if accound id is invalid -> no rows (None)

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
    acc_id = token_obj.account_id
    await db.delete(token_obj)

    # Create new tokens
    # lets fetch account + roles from db again, as we cant jwt (maybe be tampered or expired)
    query = (
        select(Account.id, Seller.seller_id, DeliveryPartner.delivery_partner_id)
        .outerjoin(Seller, Account.id == Seller.seller_id)
        .outerjoin(DeliveryPartner, Account.id == DeliveryPartner.delivery_partner_id)
        .where(Account.id == acc_id)
    )
    res = (await db.execute(query)).first()
    if res is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Refresh Token / User",
        )
    roles: list[str] = []
    if res.seller_id is not None:
        roles.append(UserRole.SELLER)
    if res.delivery_partner_id is not None:
        roles.append(UserRole.DELIVERY_PARTNER)

    # create jwt tokens
    jwt_token = create_access_token(subject=str(res.id), roles=roles)
    raw_refresh_token = create_refresh_token()
    hashed_refresh_token = hash_refresh_token(raw_refresh_token)
    expires_at = get_refresh_token_expiry()

    add_refresh_token = RefreshToken(
        account_id=res.id, token_hash=hashed_refresh_token, expires_at=expires_at
    )
    db.add(add_refresh_token)
    await db.commit()
    await db.refresh(add_refresh_token)

    return {
        "access_token": jwt_token,
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
