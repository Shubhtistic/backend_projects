from uuid import UUID
from app.dependancies.db_dependancy import DbSessionDep
from fastapi import APIRouter, HTTPException, status
from sqlalchemy.future import select
from sqlalchemy import delete
from app.schemas.shipment import CreateShipment, ReadShipment, UpdateShipment
from app.database.db_models import Shipment
from app.dependancies.auth import CurrentUserDep
from app.service.shipment_service import ShipmentService

shipment_service = ShipmentService()
router = APIRouter(prefix="/shipment")


@router.post("/create", response_model=ReadShipment)
async def create_shipment(
    user: CurrentUserDep, shipment: CreateShipment, db: DbSessionDep
):
    res = await shipment_service.create_new_shipment(db, shipment, user)
    return res


@router.get("/{shipment_id}", response_model=ReadShipment)
async def get_shipment(user: CurrentUserDep, shipment_id: UUID, db: DbSessionDep):
    res = await shipment_service.get_shipment(db, shipment_id, user)
    return res


@router.patch("/{shipment_id}", response_model=ReadShipment)
async def update_shipment(
    user: CurrentUserDep,
    shipment_id: UUID,
    shipment_update: UpdateShipment,
    db: DbSessionDep,
):
    res = await shipment_service.update_shipment(db, shipment_id, shipment_update, user)
    return res


@router.delete("/{shipment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shipment(user: CurrentUserDep, shipment_id: UUID, db: DbSessionDep):
    await shipment_service.delete_shipment(db, shipment_id, user)
