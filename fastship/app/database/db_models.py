from enum import Enum
from sqlmodel import SQLModel, Field, Column, DateTime
from datetime import datetime, timezone, timedelta
from uuid import uuid4, UUID
from pydantic import EmailStr


class ShipmentStatus(str, Enum):  # using str, enum makes it behave like enum
    Pending = "Pending"
    InTransit = "InTransit"
    Delivered = "Delivered"


class Shipment(SQLModel, table=True):
    __tablename__ = "shipment"  # if not mentioned defaults to class name in lowercase

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    content: str = Field(max_length=50)
    weight: float
    destination: int
    status: ShipmentStatus = Field(default=ShipmentStatus.Pending)

    estimated_delivery: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=5),
        sa_column=Column(DateTime(timezone=True)),
    )
    # # sa_column tells sqlmodel to use a specific SQLAlchemy column type
    # DateTime(timezone=True) creates a 'TIMESTAMPTZ' column in Postgres


class Seller(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    email: EmailStr = Field(unique=True)
    hashed_password: str


class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_token"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    user_id: UUID = Field(foreign_key="seller.id", index=True)

    token_hash: str

    expires_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True)),
    )

    revoked: bool = Field(default=False)
