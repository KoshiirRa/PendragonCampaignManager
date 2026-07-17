# Migrations

Numbered SQL files are the source of truth and are independently runnable with `psql`.
Alembic revisions in `versions/` invoke the same files, keeping CLI and Supabase workflows aligned.
Use `py -3.12 -m alembic upgrade head` when applying migrations through the application toolchain.
