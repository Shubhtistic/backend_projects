from uuid import UUID
from app.database.db_models import Seller, Shipment
from app.schemas.enums import UserRole
from app.dependancies.auth import CurrentUserDep
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from fastapi import HTTPException, status
from app.service.shipment_event_log import ShipmentEventService

shipment_event_log = ShipmentEventService()


class ShipmentService:

    async def create_new_shipment(
        self, session: AsyncSession, shipment_data, user: CurrentUserDep
    ):
        if UserRole.SELLER not in user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not a seller"
            )

        seller = (
            await session.execute(
                select(Seller.seller_address, Seller.seller_zip_code).where(
                    Seller.seller_id == user.account.id
                )
            )
        ).one_or_none()

        if seller is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Seller not found"
            )

        new_shipment = Shipment(
            content=shipment_data.content,
            weight=shipment_data.weight,
            destination_address=shipment_data.destination_address,
            destination_zip=shipment_data.destination_zip,
            seller_id=user.account.id,
        )
        session.add(new_shipment)
        await session.flush()

        await shipment_event_log.log_event(
            session=session,
            shipment_id=new_shipment.id,
            desc=f"Shipment created by seller {user.account.id}",
            current_location=seller.seller_address,
            current_location_zip=seller.seller_zip_code,
        )
        await session.commit()
        return new_shipment

    async def get_shipment(
        self, session: AsyncSession, shipment_id: UUID, user: CurrentUserDep
    ):
        res = (
            await session.execute(select(Shipment).where(Shipment.id == shipment_id))
        ).scalar_one_or_none()

        if not res:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Shipment not found"
            )

        if (
            res.seller_id != user.account.id
            and res.delivery_partner_id != user.account.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this shipment",
            )

        return res

    async def update_shipment(
        self,
        session: AsyncSession,
        shipment_id: UUID,
        update_data,
        user: CurrentUserDep,
    ):
        res = (
            await session.execute(select(Shipment).where(Shipment.id == shipment_id))
        ).scalar_one_or_none()

        if not res:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Shipment not found"
            )

        # only seller can update their own shipment
        if res.seller_id != user.account.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not your shipment"
            )

        data = update_data.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(res, key, value)

        await shipment_event_log.log_event(
            session=session,
            shipment_id=res.id,
            desc=f"Shipment updated — fields changed: {list(data.keys())}",
            current_location=res.destination_address,
            current_location_zip=res.destination_zip,
        )

        await session.commit()
        await session.refresh(res)
        return res

    async def delete_shipment(
        self, session: AsyncSession, shipment_id: UUID, user: CurrentUserDep
    ):
        res = (
            await session.execute(select(Shipment).where(Shipment.id == shipment_id))
        ).scalar_one_or_none()

        if not res:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Shipment not found"
            )

        if res.seller_id != user.account.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not your shipment"
            )

        # log before delete — cascade will wipe events after
        await shipment_event_log.log_event(
            session=session,
            shipment_id=res.id,
            desc="Shipment deleted by seller",
            current_location=res.destination_address,
            current_location_zip=res.destination_zip,
        )

        await session.delete(res)
        await session.commit()
