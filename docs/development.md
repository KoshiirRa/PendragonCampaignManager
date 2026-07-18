# Development guide

Keep each domain as a vertical slice: numbered SQL migration, ORM mapping, request/response schemas, services, routes, and tests. Do not introduce mutable summary columns where a ledger or effective-dated history can reconstruct the value.

Before merging a slice, run:

```powershell
py -3.12 -m ruff format .
py -3.12 -m ruff check .
py -3.12 -m pytest -q
py -3.12 -m alembic heads
py -3.12 -m compileall -q app migrations tests
py -3.12 scripts/sync_supabase_migrations.py --check
```

Export the committed API contract after changing routes or schemas:

```powershell
py -3.12 scripts/export_openapi.py
```

The SQL migrations remain the deployment source of truth for Supabase. Alembic owns model-drift detection and future generated revisions; never edit an already deployed numbered migration.

When the player chronicle changes, also validate its independent toolchain:

```powershell
Set-Location frontend
npm ci
npm run lint
npm run build
```
