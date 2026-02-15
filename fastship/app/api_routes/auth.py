from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends
from fastapi import status, HTTPException

from app.dependancies.db_dependancy import DbSessionDep
from app.schemas.user_auth import CreateUser, ReadUser
from sqlalchemy.future import select
from app.database.db_models import Seller
from app.security.utils import verify_hash_password, generate_hash

router = APIRouter(prefix="/Auth")


@router.post("/register", response_model=ReadUser)
async def register_user(user: CreateUser, db: DbSessionDep):
    ## check if email already exists

    qry = select(Seller).where(Seller.email == user.email)

    res = await db.execute(qry)
    existing_seller = res.scalar_one_or_none()
    if existing_seller is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="the user already exists"
        )

    hashed_password = generate_hash(user.password)

    # new_user=user.model_dump()
    # ## convert pydantic schema to db

    new_seller = Seller(
        name=user.name, email=user.email, hashed_password=hashed_password
    )
    db.add(new_seller)
    await db.commit()
    await db.refresh(new_seller)

    return new_seller
