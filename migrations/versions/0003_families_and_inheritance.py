"""Families, inheritance, and ancestral history.

Revision ID: 0003_families_and_inheritance
Revises: 0002_characters_and_manors
"""

from collections.abc import Sequence
from pathlib import Path

from alembic import op

revision: str = "0003_families_and_inheritance"
down_revision: str | None = "0002_characters_and_manors"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SQL_ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS = ("009_families.sql", "010_inheritance.sql", "011_ancestral_history.sql")


def _execute_script(sql: str) -> None:
    adapted_connection = op.get_bind().connection.dbapi_connection
    adapted_connection.run_async(lambda driver: driver.execute(sql))


def upgrade() -> None:
    for filename in MIGRATIONS:
        _execute_script((SQL_ROOT / filename).read_text(encoding="utf-8"))


def downgrade() -> None:
    for table in (
        "family_history_entries",
        "source_references",
        "inheritance_manor_transfers",
        "inheritance_heirs",
        "inheritance_cases",
        "marriages",
        "character_parentage",
        "family_memberships",
        "families",
    ):
        op.execute(f"DROP TABLE IF EXISTS {table}")
