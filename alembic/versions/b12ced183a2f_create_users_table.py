"""create users table

Revision ID: b12ced183a2f
Revises: 
Create Date: 2026-07-22 08:38:59.530900

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b12ced183a2f'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),

        sa.Column(
            "first_name",
            sa.String(length=512),
            nullable=False
        ),

        sa.Column(
            "last_name",
            sa.String(length=512),
            nullable=False
        ),

        sa.Column(
            "middle_name",
            sa.String(length=512),
            nullable=True
        ),

        sa.Column(
            "email",
            sa.String(length=512),
            nullable=False
        ),


        sa.Column(
            "hashed_password",
            sa.String(length=512),
            nullable=False
        ) 
    )



def downgrade() -> None:
    """Downgrade schema."""
    
    op.drop_table("news")
