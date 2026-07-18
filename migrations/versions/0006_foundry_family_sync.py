"""Foundry family synchronization identities.

Revision ID: 0006_foundry_family_sync
Revises: 0005_character_possessions
"""

from collections.abc import Sequence
from pathlib import Path

from alembic import op
from sqlalchemy import inspect

revision: str = "0006_foundry_family_sync"
down_revision: str | None = "0005_character_possessions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None
SQL_ROOT = Path(__file__).resolve().parents[1]


def _execute_script(sql: str) -> None:
    adapted_connection = op.get_bind().connection.dbapi_connection
    adapted_connection.run_async(lambda driver: driver.execute(sql))


def upgrade() -> None:
    columns = {column["name"] for column in inspect(op.get_bind()).get_columns("marriages")}
    if "source_key" not in columns:
        _execute_script((SQL_ROOT / "014_foundry_family_sync.sql").read_text(encoding="utf-8"))


def downgrade() -> None:
    for table in (
        "inheritance_heirs",
        "inheritance_cases",
        "marriages",
        "character_parentage",
        "family_memberships",
    ):
        op.execute(f"ALTER TABLE {table} DROP COLUMN IF EXISTS source_key")
