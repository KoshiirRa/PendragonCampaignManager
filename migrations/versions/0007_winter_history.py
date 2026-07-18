"""Winter phases and Foundry character history.

Revision ID: 0007_winter_history
Revises: 0006_foundry_family_sync
"""

from collections.abc import Sequence
from pathlib import Path

from alembic import op
from sqlalchemy import inspect

revision: str = "0007_winter_history"
down_revision: str | None = "0006_foundry_family_sync"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None
SQL_ROOT = Path(__file__).resolve().parents[1]


def _execute_script(sql: str) -> None:
    adapted_connection = op.get_bind().connection.dbapi_connection
    adapted_connection.run_async(lambda driver: driver.execute(sql))


def upgrade() -> None:
    if "winter_phases" not in inspect(op.get_bind()).get_table_names():
        _execute_script((SQL_ROOT / "015_winter_history.sql").read_text(encoding="utf-8"))


def downgrade() -> None:
    for table in (
        "character_wound_ledger",
        "winter_phase_participants",
        "winter_phases",
        "character_history_entries",
    ):
        op.execute(f"DROP TABLE IF EXISTS {table}")
