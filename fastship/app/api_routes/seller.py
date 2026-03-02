from app.dependancies.db_dependancy import DbSessionDep
from app.dependancies.auth import CurrentUserDep
from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.future import select
from sqlalchemy import join
from app.database.db_models import Account, Seller
from app.schemas.seller import RegisterSeller

router = APIRouter()


@router.post("/seller", response_model=RegisterSeller)
async def register_seller(db: DbSessionDep, user: CurrentUserDep):
    """Register the user as an Seller"""
    ## we have the user already logged in so we will use the dependancy to get info

    seller_id = user.account.id
    qry = select(Seller.seller_id).where(Seller.seller_id == user.account.id)
    res = (await db.execute(qry)).scalar_one_or_none()

    if res is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The Current User is already a Seller",
        )

    # lets add new user
    new_seller = Seller(seller_id=user.account.id)
    db.add(new_seller)
    await db.commit()
    await db.refresh(new_seller)

    return user.account
