# Migrations

Numbered SQL files are the source of truth and are independently runnable with `psql`.
Alembic revisions in `versions/` invoke the same files, keeping CLI and Supabase workflows aligned.
Use `py -3.12 -m alembic upgrade head` when applying migrations through the application toolchain.

The numbered SQL files in this directory are canonical. Run
`py -3.12 scripts/sync_supabase_migrations.py` after changing one; generated copies under
`supabase/migrations/` are required by the Supabase CLI. CI and tests should use `--check` to
reject drift.
