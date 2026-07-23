"""is_active for user

Revision ID: f2ce873f717a
Revises: ba70ef45e667
Create Date: 2026-07-23 16:22:55.953489

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f2ce873f717a'
down_revision: Union[str, Sequence[str], None] = 'ba70ef45e667'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "users", 
        sa.Column("is_active", sa.Boolean, server_default=sa.text('true'), nullable=False)
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column("users", "is_active")
