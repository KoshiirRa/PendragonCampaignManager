# Development guide

Keep each domain as a vertical slice: numbered SQL migration, ORM mapping, request/response schemas, services, routes, and tests. Do not introduce mutable summary columns where a ledger or effective-dated history can reconstruct the value.

Before merging a slice, run:

```powershell
ruff check .
pytest
```

Export the committed API contract after changing routes or schemas:

```powershell
py -3.12 scripts/export_openapi.py
```

The SQL migrations remain the deployment source of truth for Supabase. Alembic owns model-drift detection and future generated revisions; never edit an already deployed numbered migration.
