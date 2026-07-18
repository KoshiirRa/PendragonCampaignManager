"""Apply the idempotent frontend demo seed to an explicitly configured database."""

import asyncio
import os
from pathlib import Path

import asyncpg


async def main() -> None:
    database_url = os.environ["DATABASE_URL"].replace("postgresql+asyncpg://", "postgresql://")
    seed_dir = Path(__file__).parents[1] / "seed"
    scripts = [seed_dir / "005_salisbury_campaign_slug.sql"]
    scripts.extend(
        script
        for script in sorted(seed_dir.glob("[0-9][0-9][0-9]_*.sql"))
        if script.name != "005_salisbury_campaign_slug.sql"
    )
    connection = await asyncpg.connect(database_url)
    try:
        for script in scripts:
            await connection.execute(script.read_text())
        campaign = await connection.fetchrow("SELECT id FROM campaigns WHERE slug = 'salisbury'")
    finally:
        await connection.close()
    if campaign is None:
        raise RuntimeError("Development campaign was not found; seed was not applied")
    print(f"Seeded development campaign {campaign['id']}")


if __name__ == "__main__":
    asyncio.run(main())
