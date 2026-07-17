from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIGRATION_MAP = {
    ROOT / "migrations/001_extensions.sql": ROOT
    / "supabase/migrations/202607170001_extensions.sql",
    ROOT / "migrations/002_campaign.sql": ROOT / "supabase/migrations/202607170002_campaign.sql",
    ROOT / "migrations/003_events.sql": ROOT / "supabase/migrations/202607170003_events.sql",
    ROOT / "migrations/004_dice_logs.sql": ROOT / "supabase/migrations/202607170004_dice_logs.sql",
    ROOT / "migrations/005_characters.sql": ROOT
    / "supabase/migrations/202607170005_characters.sql",
    ROOT / "migrations/006_character_values.sql": ROOT
    / "supabase/migrations/202607170006_character_values.sql",
    ROOT / "migrations/007_glory.sql": ROOT / "supabase/migrations/202607170007_glory.sql",
    ROOT / "migrations/008_locations_manors.sql": ROOT
    / "supabase/migrations/202607170008_locations_manors.sql",
    ROOT / "migrations/009_families.sql": ROOT / "supabase/migrations/202607170009_families.sql",
    ROOT / "migrations/010_inheritance.sql": ROOT
    / "supabase/migrations/202607170010_inheritance.sql",
    ROOT / "migrations/011_ancestral_history.sql": ROOT
    / "supabase/migrations/202607170011_ancestral_history.sql",
}
SEED_SOURCES = (ROOT / "seed/001_campaign.sql", ROOT / "seed/002_characters_and_manor.sql")
SEED_DESTINATION = ROOT / "supabase/seed.sql"


def synchronize(*, check: bool) -> bool:
    synchronized = True
    for source, destination in MIGRATION_MAP.items():
        expected = source.read_bytes()
        actual = destination.read_bytes() if destination.exists() else None
        if actual == expected:
            continue
        synchronized = False
        if not check:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(expected)
            print(f"Synchronized {destination.relative_to(ROOT)}")
        else:
            print(f"Out of date: {destination.relative_to(ROOT)}", file=sys.stderr)
    expected_seed = b"\n".join(source.read_bytes().rstrip() for source in SEED_SOURCES) + b"\n"
    actual_seed = SEED_DESTINATION.read_bytes() if SEED_DESTINATION.exists() else None
    if actual_seed != expected_seed:
        synchronized = False
        if not check:
            SEED_DESTINATION.write_bytes(expected_seed)
            print(f"Synchronized {SEED_DESTINATION.relative_to(ROOT)}")
        else:
            print(f"Out of date: {SEED_DESTINATION.relative_to(ROOT)}", file=sys.stderr)
    return synchronized


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Synchronize canonical SQL migrations into the Supabase CLI layout."
    )
    parser.add_argument("--check", action="store_true", help="Fail instead of writing files.")
    args = parser.parse_args()
    synchronized = synchronize(check=args.check)
    return 0 if synchronized or not args.check else 1


if __name__ == "__main__":
    raise SystemExit(main())
