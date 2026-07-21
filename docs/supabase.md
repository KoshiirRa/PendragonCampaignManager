# Supabase database workflow

The hosted project is linked locally through the Supabase CLI. Project references are not secrets, but database passwords, access tokens, connection strings, and service-role keys must never be committed or included in support output.

## Source of truth

Incremental SQL files under `migrations/` remain canonical. Supabase requires migrations under `supabase/migrations/`, so a deterministic synchronization script produces byte-identical copies:

```powershell
py -3.12 scripts/sync_supabase_migrations.py
py -3.12 scripts/sync_supabase_migrations.py --check
```

Never edit the generated Supabase copies directly. Add a new canonical numbered migration, extend `MIGRATION_MAP`, synchronize, and test.

## Data API security boundary

Migration `019_secure_public_schema.sql` enables Row-Level Security on every existing table in the
`public` schema and removes all table and sequence privileges from Supabase's `anon` and
`authenticated` roles. It deliberately creates no policies: direct PostgREST/Data API access is
deny-by-default because FastAPI is the only supported database boundary. It also changes default
privileges for objects subsequently created by the migration role.

The Cloud Run application uses a direct PostgreSQL connection owned by a trusted database role;
RLS is not forced on table owners. Never place that connection string or a Supabase service-role key
in browser, Foundry, Custom GPT, frontend, or source-control configuration. New migrations must
continue to be followed by the security migration's default-privilege posture; if a different owner
creates objects, explicitly review its default privileges before deployment.

This migration is intentionally irreversible. Re-enabling direct Data API access requires a new,
reviewed migration with campaign-scoped policies and explicit grants; do not disable RLS as a
rollback shortcut.

## Inspect before applying

These commands are read-only:

```powershell
npx supabase@latest migration list --linked
npx supabase@latest db push --linked --dry-run
```

Review the exact pending versions before any push. Do not use `db reset` against a linked hosted project.

After applying a security migration, rerun the Supabase Security Advisor and verify that both
`rls_disabled_in_public` and `sensitive_columns_exposed` findings are cleared.

## Apply migrations

Applying migrations is an external database change and requires explicit approval:

```powershell
npx supabase@latest db push --linked
```

Seed data is separate and must not be applied to a real campaign database automatically. Use `--include-seed` only for a disposable development project after explicit confirmation.

## Cloud Run connection

Use the Supabase dashboard's **Connect** panel to obtain a session-pooler connection string. Convert its scheme to `postgresql+asyncpg://` before storing it as the `pendragon-database-url` Secret Manager secret. Do not put it in `.env.example`, Cloud Build substitutions, or GitHub Actions output.
