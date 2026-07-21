from pathlib import Path

from scripts.sync_supabase_migrations import (
    MIGRATION_MAP,
    SEED_DESTINATION,
    SEED_SOURCES,
)


def test_supabase_files_match_canonical_sql() -> None:
    for source, destination in MIGRATION_MAP.items():
        assert destination.read_bytes() == source.read_bytes()


def test_supabase_migrations_have_ordered_versions() -> None:
    versions = [path.name.split("_", 1)[0] for path in Path("supabase/migrations").glob("*.sql")]
    assert versions == sorted(versions)
    assert len(versions) == len(set(versions))


def test_supabase_seed_combines_canonical_seed_files() -> None:
    expected = b"\n".join(source.read_bytes().rstrip() for source in SEED_SOURCES) + b"\n"
    assert SEED_DESTINATION.read_bytes() == expected


def test_security_migration_enables_rls_and_removes_data_api_privileges() -> None:
    sql = Path("migrations/019_secure_public_schema.sql").read_text(encoding="utf-8")

    assert "ENABLE ROW LEVEL SECURITY" in sql
    assert "REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public" in sql
    assert "REVOKE ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public" in sql
    assert "ALTER DEFAULT PRIVILEGES IN SCHEMA public" in sql
    assert "anon" in sql
    assert "authenticated" in sql
    assert "CREATE POLICY" not in sql
