"""Create the initial Stitch Bunny tables.

Revision ID: bd2eec4dbc2c
Revises:
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "bd2eec4dbc2c"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

JSON_TYPE = sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql")


def upgrade() -> None:
    op.create_table(
        "images",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(length=128), nullable=False),
        sa.Column("storage_key", sa.String(length=255), nullable=False),
        sa.Column("mime_type", sa.String(length=100), nullable=False),
        sa.Column("width", sa.Integer(), nullable=False),
        sa.Column("height", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("storage_key"),
    )
    op.create_index(op.f("ix_images_user_id"), "images", ["user_id"], unique=False)
    op.create_table(
        "measurements",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("data", JSON_TYPE, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_measurements_user_id"), "measurements", ["user_id"], unique=False)
    op.create_table(
        "patterns",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("garment", sa.String(length=50), nullable=False),
        sa.Column("data", JSON_TYPE, nullable=False),
        sa.Column("is_public", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_patterns_user_id"), "patterns", ["user_id"], unique=False)
    op.create_table(
        "traces",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("image_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(length=128), nullable=False),
        sa.Column("points", JSON_TYPE, nullable=False),
        sa.Column("label", sa.String(length=50), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("suggestions", JSON_TYPE, nullable=False),
        sa.Column("note", sa.String(length=500), nullable=True),
        sa.Column("confirmed_by_user", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["image_id"], ["images.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_traces_image_id"), "traces", ["image_id"], unique=False)
    op.create_index(op.f("ix_traces_user_id"), "traces", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_traces_user_id"), table_name="traces")
    op.drop_index(op.f("ix_traces_image_id"), table_name="traces")
    op.drop_table("traces")
    op.drop_index(op.f("ix_patterns_user_id"), table_name="patterns")
    op.drop_table("patterns")
    op.drop_index(op.f("ix_measurements_user_id"), table_name="measurements")
    op.drop_table("measurements")
    op.drop_index(op.f("ix_images_user_id"), table_name="images")
    op.drop_table("images")
