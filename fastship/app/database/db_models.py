from enum import Enum
from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import uuid4, UUID


class ShipmentStatus(str, Enum):  # using str, enum makes it behave like enum
    Pending = "Pending"
    InTransit = "InTransit"
    Delivered = "Delivered"


class Shipment(SQLModel, table=True):
    __tablename__ = "shipment"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    content: str = Field(max_length=50)
    weight: float
    destination: int
    estimated_delivery: datetime
