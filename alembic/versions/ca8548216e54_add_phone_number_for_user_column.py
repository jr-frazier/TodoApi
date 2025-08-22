"""Add phone_number for user column

Revision ID: ca8548216e54
Revises: 
Create Date: 2025-08-19 16:17:29.811835

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ca8548216e54'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('phone_number', sa.String(length=15), nullable=True))

def downgrade() -> None:
    op.drop_column('users', 'phone_number')

