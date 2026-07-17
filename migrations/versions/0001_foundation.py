"""Campaign, session, event timeline, and dice-log foundation.

Revision ID: 0001_foundation
Revises:
"""

from collections.abc import Sequence
from pathlib import Path

from alembic import op

revision: str = "0001_foundation"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SQL_ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS = (
    "001_extensions.sql",
    "002_campaign.sql",
    "003_events.sql",
    "004_dice_logs.sql",
)


def _execute_script(sql: str) -> None:
    """Run a multi-statement SQL file through asyncpg's native connection."""
    adapted_connection = op.get_bind().connection.dbapi_connection
    adapted_connection.run_async(lambda driver: driver.execute(sql))


def upgrade() -> None:
    for filename in MIGRATIONS:
        _execute_script((SQL_ROOT / filename).read_text(encoding="utf-8"))


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS dice_logs")
    op.execute("DROP TABLE IF EXISTS event_links")
    op.execute("DROP TABLE IF EXISTS events")
    op.execute("DROP TYPE IF EXISTS event_visibility")
    op.execute("DROP TABLE IF EXISTS campaign_sessions")
    op.execute("DROP TABLE IF EXISTS campaigns")
    op.execute("DROP FUNCTION IF EXISTS set_updated_at()")
