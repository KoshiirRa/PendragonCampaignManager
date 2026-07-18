"""Manor economics and households.

Revision ID: 0008_manor_economics
Revises: 0007_winter_history
"""

from collections.abc import Sequence
from pathlib import Path

from alembic import op
from sqlalchemy import inspect

revision: str = "0008_manor_economics"
down_revision: str | None = "0007_winter_history"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None
SQL_ROOT = Path(__file__).resolve().parents[1]


def _execute_script(sql: str) -> None:
    connection = op.get_bind().connection.dbapi_connection
    connection.run_async(lambda driver: driver.execute(sql))


def upgrade() -> None:
    if "manor_annual_resolutions" not in inspect(op.get_bind()).get_table_names():
        _execute_script(
            (SQL_ROOT / "016_manor_economics_households.sql").read_text(encoding="utf-8")
        )


def downgrade() -> None:
    for table in (
        "manor_defense_layers",
        "household_employment_history",
        "manor_asset_ledger",
        "manor_assets",
        "manor_treasury_ledger",
        "manor_annual_resolutions",
    ):
        op.execute(f"DROP TABLE IF EXISTS {table}")
    for column in ("base_defensive_value", "population", "assized_rent"):
        op.execute(f"ALTER TABLE manors DROP COLUMN IF EXISTS {column}")
