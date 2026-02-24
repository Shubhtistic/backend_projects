from enum import Enum
from sqlmodel import SQLModel, Field, Column, DateTime, Relationship, ARRAY, String
from datetime import datetime, timezone, timedelta
from uuid import uuid4, UUID
from pydantic import EmailStr


class ShipmentStatus(str, Enum):  # using str, enum makes it behave like enum
    Pending = "Pending"
    InTransit = "InTransit"
    Delivered = "Delivered"


class Account(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=50)
    email: EmailStr
    hashed_password: str

    seller: "Seller" = Relationship(back_populates="account")
    delivery_partner: "DeliveryPartener" = Relationship(back_populates="account")
    refresh_tokens: list["RefreshToken"] = Relationship(
        back_populates="account", sa_relationship_kwargs={"cascade": "all, delete"}
    )


class Seller(SQLModel, table=True):
    seller_id: UUID = Field(foreign_key="account.id", primary_key=True)

    account: Account = Relationship(back_populates="seller")

    shipment: list["Shipment"] = Relationship(back_populates="seller")


class DeliveryPartener(SQLModel, table=True):
    __tablename__ = "delivery_partner"

    id: UUID = Field(foreign_key="account.id", primary_key=True)

    account: Account = Relationship(back_populates="delivery_partner")

    deliverable_zip_codes: list[str] = Field(sa_column=Column(ARRAY(String)))
    max_handling_capacity: int

    shipment: list["Shipment"] = Relationship(back_populates="delivery_partner")


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

    seller_id: UUID = Field(foreign_key="seller.seller_id")
    delivery_partner_id: UUID = Field(foreign_key="delivery_partner.id")

    # relationship
    seller: "Seller" = Relationship(back_populates="shipment")
    delivery_partner: "DeliveryPartener" = Relationship(back_populates="shipment")


class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_token"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    account_id: UUID = Field(foreign_key="account.id", index=True)

    token_hash: str

    expires_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True)),
    )

    revoked: bool = Field(default=False)

    account: Account = Relationship(back_populates="refresh_tokens")
