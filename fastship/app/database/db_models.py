from enum import Enum
from sqlmodel import SQLModel, Field, Column, DateTime, Relationship, ARRAY, String
from sqlalchemy import Enum as SAEnum
from datetime import datetime, timezone, timedelta
from uuid_utils import uuid7
from uuid import UUID
from pydantic import EmailStr

from app.schemas.enums import ShipmentStatus, Status


class Account(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid7, primary_key=True)
    name: str = Field(max_length=50)
    email: EmailStr = Field(unique=True, index=True)
    hashed_password: str

    ## when was account created
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True)),
    )
    is_active: bool = Field(default=True)
    # is the user active or banned
    # we can use this as foreign key also
    # is user is banned then user as a seller and as a delivery agent will also be banned

    seller: "Seller" = Relationship(back_populates="account")
    delivery_partner: "DeliveryPartner" = Relationship(back_populates="account")
    refresh_tokens: list["RefreshToken"] = Relationship(
        back_populates="account", sa_relationship_kwargs={"cascade": "all, delete"}
    )


class Seller(SQLModel, table=True):
    seller_id: UUID = Field(foreign_key="account.id", primary_key=True)
    # primary key has an idex by default

    # when did they became a seller
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True)),
    )
    status: Status = Field(
        default=Status.Pending,
        sa_column=Column(SAEnum(Status, name="seller_status_enum"), nullable=False),
    )
    seller_address: str
    seller_zip_code: str
    account: Account = Relationship(back_populates="seller")

    shipment: list["Shipment"] = Relationship(back_populates="seller")


class DeliveryPartner(SQLModel, table=True):
    __tablename__ = "delivery_partner"

    delivery_partner_id: UUID = Field(foreign_key="account.id", primary_key=True)
    deliverable_zip_codes: list[str] = Field(sa_column=Column(ARRAY(String)))
    max_handling_capacity: int

    # when did they become a deliverypartner
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True)),
    )
    status: Status = Field(
        default=Status.Pending,
        sa_column=Column(
            SAEnum(Status, name="delivery_partner_status_enum"), nullable=False
        ),
    )

    account: Account = Relationship(back_populates="delivery_partner")

    shipment: list["Shipment"] = Relationship(back_populates="delivery_partner")


class Shipment(SQLModel, table=True):
    __tablename__ = "shipment"  # if not mentioned defaults to class name in lowercase

    id: UUID = Field(default_factory=uuid7, primary_key=True)
    content: str = Field(max_length=50)
    weight: float
    destination_address: str
    destination_zip: str
    status: ShipmentStatus = Field(
        default=ShipmentStatus.Pending,
        sa_column=Column(
            SAEnum(ShipmentStatus, name="shipment_status_enum"), nullable=False
        ),
    )

    estimated_delivery: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=5),
        sa_column=Column(DateTime(timezone=True)),
    )
    # # sa_column tells sqlmodel to use a specific SQLAlchemy column type
    # DateTime(timezone=True) creates a 'TIMESTAMPTZ' column in Postgres

    seller_id: UUID = Field(foreign_key="seller.seller_id", index=True)
    delivery_partner_id: UUID | None = Field(
        default=None, foreign_key="delivery_partner.delivery_partner_id", index=True
    )

    # relationship
    seller: "Seller" = Relationship(back_populates="shipment")
    delivery_partner: "DeliveryPartner" = Relationship(back_populates="shipment")
    timeline: list["ShipmentEvent"] = Relationship(
        back_populates="shipment", sa_relationship_kwargs={"cascade": "all, delete"}
    )


class ShipmentEvent(SQLModel, table=True):
    __tablename__ = "shipment_event"
    event_id: UUID = Field(default_factory=uuid7, primary_key=True)
    shipment_id: UUID = Field(foreign_key="shipment.id", index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    current_location: str
    description: str | None = Field(default=None)

    shipment: "Shipment" = Relationship(back_populates="timeline")


class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_token"

    id: UUID = Field(default_factory=uuid7, primary_key=True)

    account_id: UUID = Field(foreign_key="account.id", index=True)

    token_hash: str = Field(index=True)

    expires_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True)),
    )

    revoked: bool = Field(default=False)

    account: Account = Relationship(back_populates="refresh_tokens")


Account.model_rebuild()
Seller.model_rebuild()
DeliveryPartner.model_rebuild()
Shipment.model_rebuild()
RefreshToken.model_rebuild()
ShipmentEvent.model_rebuild()
## we use forward reference when classes dont exist yet in that specific code
# model rebuild tells them -> now all classes are defined , lets resolve all forward refs
