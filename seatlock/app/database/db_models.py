from datetime import datetime, timezone
from uuid import UUID
from sqlmodel import SQLModel, Field, Column, Relationship
from sqlalchemy import DateTime, ForeignKey
from uuid_utils import uuid7


class Users(SQLModel, table=True):
    __tablename__ = "users"

    user_id: UUID = Field(default_factory=uuid7, primary_key=True)
    first_name: str = Field(nullable=False, max_length=30)
    last_name: str = Field(nullable=False, max_length=30)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    mobile_no: str = Field(unique=True, max_length=15)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True)),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc)
        ),
    )
    refresh_tokens: list["RefreshToken"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_tokens"

    id: UUID = Field(default_factory=uuid7, primary_key=True)
    user_id: UUID = Field(
        sa_column=Column(
            ForeignKey("users.user_id", ondelete="CASCADE"), index=True, nullable=False
        )
    )
    hashed_token: str = Field(index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True)),
    )
    expiry_date: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    is_revoked: bool = Field(default=False)
    user: "Users" = Relationship(back_populates="refresh_tokens")
