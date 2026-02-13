"""add preview path to file

Revision ID: 7d8e9f0a1b2c
Revises: e17a8f2ff712
Create Date: 2026-02-13 13:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7d8e9f0a1b2c'
down_revision: Union[str, None] = 'e17a8f2ff712'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('files', sa.Column('preview_path', sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column('files', 'preview_path')
