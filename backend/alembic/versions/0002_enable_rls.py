"""Enable row level security on application tables in PostgreSQL.

Revision ID: 0002enablerls
Revises: bd2eec4dbc2c
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0002enablerls"
down_revision: Union[str, Sequence[str], None] = "bd2eec4dbc2c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLES = ("images", "traces", "patterns", "measurements", "alembic_version")


def upgrade() -> None:
    if op.get_bind().dialect.name != "postgresql":
        return
    for table in TABLES:
        op.execute(f'ALTER TABLE public."{table}" ENABLE ROW LEVEL SECURITY')


def downgrade() -> None:
    if op.get_bind().dialect.name != "postgresql":
        return
    for table in TABLES:
        op.execute(f'ALTER TABLE public."{table}" DISABLE ROW LEVEL SECURITY')
