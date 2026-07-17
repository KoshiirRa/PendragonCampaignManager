"""Characters, values, Glory, locations, and manors.

Revision ID: 0002_characters_and_manors
Revises: 0001_foundation
"""

from collections.abc import Sequence
from pathlib import Path

from alembic import op

revision: str = "0002_characters_and_manors"
down_revision: str | None = "0001_foundation"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SQL_ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS = (
    "005_characters.sql",
    "006_character_values.sql",
    "007_glory.sql",
    "008_locations_manors.sql",
)


def _execute_script(sql: str) -> None:
    adapted_connection = op.get_bind().connection.dbapi_connection
    adapted_connection.run_async(lambda driver: driver.execute(sql))


def upgrade() -> None:
    for filename in MIGRATIONS:
        _execute_script((SQL_ROOT / filename).read_text(encoding="utf-8"))


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS manor_improvement_ledger")
    op.execute("DROP TABLE IF EXISTS manor_improvements")
    op.execute("DROP TABLE IF EXISTS manor_tenures")
    op.execute("DROP TABLE IF EXISTS manors")
    op.execute("DROP TABLE IF EXISTS location_connections")
    op.execute("DROP TABLE IF EXISTS locations")
    op.execute("DROP TYPE IF EXISTS location_kind")
    op.execute("DROP TABLE IF EXISTS glory_ledger")
    op.execute("DROP TABLE IF EXISTS character_passion_ledger")
    op.execute("DROP TABLE IF EXISTS character_passions")
    op.execute("DROP TABLE IF EXISTS character_skill_ledger")
    op.execute("DROP TABLE IF EXISTS skill_definitions")
    op.execute("DROP TABLE IF EXISTS character_trait_ledger")
    op.execute("DROP TABLE IF EXISTS trait_definitions")
    op.execute("DROP TABLE IF EXISTS character_notes")
    op.execute("DROP TABLE IF EXISTS character_status_ledger")
    op.execute("DROP FUNCTION IF EXISTS refresh_character_current_status()")
    op.execute("DROP TABLE IF EXISTS characters")
    op.execute("DROP TYPE IF EXISTS knowledge_scope")
    op.execute("DROP TYPE IF EXISTS character_status")
    op.execute("DROP TYPE IF EXISTS character_kind")
