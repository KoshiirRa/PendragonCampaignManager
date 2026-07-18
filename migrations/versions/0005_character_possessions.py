"""Character statistics, inventory, and horses.

Revision ID: 0005_character_possessions
Revises: 0004_foundry_character_sync
"""

from collections.abc import Sequence
from pathlib import Path

from alembic import op
from sqlalchemy import inspect

revision: str = "0005_character_possessions"
down_revision: str | None = "0004_foundry_character_sync"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None
SQL_ROOT = Path(__file__).resolve().parents[1]


def _execute_script(sql: str) -> None:
    adapted_connection = op.get_bind().connection.dbapi_connection
    adapted_connection.run_async(lambda driver: driver.execute(sql))


def upgrade() -> None:
    if "character_stat_ledger" in inspect(op.get_bind()).get_table_names():
        return
    _execute_script((SQL_ROOT / "013_character_possessions.sql").read_text(encoding="utf-8"))


def downgrade() -> None:
    for table in (
        "horse_stat_ledger",
        "horse_ownership_history",
        "horses",
        "character_inventory_ledger",
        "armour_profiles",
        "weapon_profiles",
        "inventory_items",
        "character_stat_ledger",
    ):
        op.execute(f"DROP TABLE IF EXISTS {table}")
