"""Change password column length

Revision ID: 2a3019e363d9
Revises: c1b12d56fa63
Create Date: 2026-03-09 18:33:36.888997

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "2a3019e363d9"
down_revision: Union[str, Sequence[str], None] = "c1b12d56fa63"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "users",
        "hashed_password",
        existing_type=sa.VARCHAR(length=60),
        type_=sa.TEXT(),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "users",
        "hashed_password",
        existing_type=sa.TEXT(),
        type_=sa.VARCHAR(length=60),
        existing_nullable=True,
    )
