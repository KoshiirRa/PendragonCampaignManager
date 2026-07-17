"""Foundry character snapshot synchronization.

Revision ID: 0004_foundry_character_sync
Revises: 0003_families_and_inheritance
"""

from collections.abc import Sequence
from pathlib import Path

from alembic import op
from sqlalchemy import inspect

revision: str = "0004_foundry_character_sync"
down_revision: str | None = "0003_families_and_inheritance"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SQL_ROOT = Path(__file__).resolve().parents[1]


def _execute_script(sql: str) -> None:
    adapted_connection = op.get_bind().connection.dbapi_connection
    adapted_connection.run_async(lambda driver: driver.execute(sql))


def upgrade() -> None:
    columns = {column["name"] for column in inspect(op.get_bind()).get_columns("trait_definitions")}
    if "source_key" in columns:
        return
    _execute_script((SQL_ROOT / "012_foundry_character_sync.sql").read_text(encoding="utf-8"))


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS character_passions_source_key_idx")
    op.execute("DROP INDEX IF EXISTS skill_definitions_source_key_idx")
    op.execute("DROP INDEX IF EXISTS trait_definitions_source_key_idx")
    op.execute("ALTER TABLE character_passions DROP COLUMN IF EXISTS source_key")
    op.execute("ALTER TABLE skill_definitions DROP COLUMN IF EXISTS source_key")
    op.execute("ALTER TABLE trait_definitions DROP COLUMN IF EXISTS source_key")
