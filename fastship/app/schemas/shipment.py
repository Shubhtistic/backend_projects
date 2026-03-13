from typing import Optional
from app.schemas.enums import ShipmentStatus
from datetime import datetime
from pydantic import BaseModel
from uuid import UUID


class CreateShipment(BaseModel):
    content: str
    weight: float
    destination_address: str
    destination_zip: str
    # no seller_id — comes from JWT


class ReadShipment(BaseModel):
    id: UUID
    content: str
    weight: float
    destination_address: str
    destination_zip: str
    status: ShipmentStatus
    estimated_delivery: datetime
    seller_id: UUID
    delivery_partner_id: UUID | None

    class Config:
        from_attributes = True


class UpdateShipment(BaseModel):
    content: Optional[str] = None
    weight: Optional[float] = None
    destination_address: Optional[str] = None
    destination_zip: Optional[str] = None
    estimated_delivery: Optional[datetime] = None
    # no status — updated via dedicated endpoint
