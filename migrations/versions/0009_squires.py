"""Squire identities, service, and state history.

Revision ID: 0009_squires
Revises: 0008_manor_economics
"""

from collections.abc import Sequence
from pathlib import Path

from alembic import op
from sqlalchemy import inspect

revision: str = "0009_squires"
down_revision: str | None = "0008_manor_economics"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None
SQL_ROOT = Path(__file__).resolve().parents[1]


def _execute_script(sql: str) -> None:
    connection = op.get_bind().connection.dbapi_connection
    connection.run_async(lambda driver: driver.execute(sql))


def upgrade() -> None:
    if "squires" not in inspect(op.get_bind()).get_table_names():
        _execute_script((SQL_ROOT / "017_squires.sql").read_text(encoding="utf-8"))


def downgrade() -> None:
    for table in ("squire_state_ledger", "squire_service_history", "squires"):
        op.execute(f"DROP TABLE IF EXISTS {table}")
