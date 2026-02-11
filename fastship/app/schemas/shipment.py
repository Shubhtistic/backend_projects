from typing import Optional
from app.database.db_models import ShipmentStatus, Field, datetime
from pydantic import BaseModel


class BaseShipment(BaseModel):
    content: str
    weight: float = Field(le=25)
    destination: int


class ReadShipment(BaseShipment):
    id: int
    status: ShipmentStatus
    estimated_delivery: datetime


class CreateShipment(BaseShipment):
    pass


class UpdateShipment(BaseModel):
    content: Optional[str]
    weight: Optional[float]
    destination: Optional[int]
    status: Optional[ShipmentStatus]
    estimated_delivery: Optional[datetime]
