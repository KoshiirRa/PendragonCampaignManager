"""Restrict the Supabase public schema to the FastAPI database boundary.

Revision ID: 0011_secure_public_schema
Revises: 0010_annual_chronicles
"""

from collections.abc import Sequence
from pathlib import Path

from alembic import op

revision: str = "0011_secure_public_schema"
down_revision: str | None = "0010_annual_chronicles"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None
SQL_ROOT = Path(__file__).resolve().parents[1]


def _execute_script(sql: str) -> None:
    connection = op.get_bind().connection.dbapi_connection
    connection.run_async(lambda driver: driver.execute(sql))


def upgrade() -> None:
    _execute_script((SQL_ROOT / "019_secure_public_schema.sql").read_text(encoding="utf-8"))


def downgrade() -> None:
    raise RuntimeError(
        "The public-schema security boundary cannot be downgraded automatically; "
        "restoring Data API access requires an explicit, reviewed policy migration."
    )
