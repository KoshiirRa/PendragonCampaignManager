"""Annual chronicles generated at Winter Phase.

Revision ID: 0010_annual_chronicles
Revises: 0009_squires
"""

from collections.abc import Sequence
from pathlib import Path

from alembic import op
from sqlalchemy import inspect

revision: str = "0010_annual_chronicles"
down_revision: str | None = "0009_squires"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None
SQL_ROOT = Path(__file__).resolve().parents[1]


def _execute_script(sql: str) -> None:
    connection = op.get_bind().connection.dbapi_connection
    connection.run_async(lambda driver: driver.execute(sql))


def upgrade() -> None:
    if "annual_chronicles" not in inspect(op.get_bind()).get_table_names():
        _execute_script((SQL_ROOT / "018_annual_chronicles.sql").read_text(encoding="utf-8"))


def downgrade() -> None:
    for table in (
        "annual_chronicle_sources",
        "annual_chronicle_sections",
        "annual_chronicles",
    ):
        op.execute(f"DROP TABLE IF EXISTS {table}")
