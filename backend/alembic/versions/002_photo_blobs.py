"""Store photo bytes in database (BLOB).

Revision ID: 002_photo_blobs
Revises: 001_initial
Create Date: 2026-06-02

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002_photo_blobs"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("user_photos", sa.Column("content", sa.LargeBinary(), nullable=True))
    op.add_column(
        "user_photos",
        sa.Column("content_type", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "user_photos",
        sa.Column("kind", sa.String(length=16), nullable=False, server_default="gallery"),
    )


def downgrade() -> None:
    op.drop_column("user_photos", "kind")
    op.drop_column("user_photos", "content_type")
    op.drop_column("user_photos", "content")
