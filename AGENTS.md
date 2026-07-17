# AGENTS.md

## Project mission

Build a production-quality, multi-campaign backend that acts as persistent memory for a Custom GPT Gamemaster running Pendragon 6th Edition campaigns across 80 or more in-game years.

This project is a long-term campaign database, not a save-file converter. Preserve historical continuity and make every important state change reconstructable.

## Technology requirements

- Python 3.12
- PostgreSQL and Supabase
- Incremental SQL migrations
- SQLAlchemy 2.x with async sessions
- Alembic
- FastAPI
- Pydantic v2
- Automatically generated OpenAPI documentation
- Pytest and Ruff

Do not replace these technologies without explicit user approval.

## Repository structure

Keep code within the established layout:

```text
migrations/     Incremental SQL migrations and Alembic revisions
app/api/        FastAPI dependencies, errors, and routes
app/models/     SQLAlchemy models
app/services/   Business logic and persistence operations
app/schemas/    Pydantic request and response models
docs/           Schema, API, ER, setup, and development documentation
tests/          Unit and integration tests
seed/           Idempotent seed data
```

Prefer one module per domain as a domain grows. Avoid unrelated utility dumping grounds.

## Required development sequence

Implement one internally consistent vertical slice at a time. For each domain:

1. Design the relational schema.
2. Document major design decisions.
3. Add an independently runnable numbered SQL migration.
4. Add or update the corresponding Alembic revision.
5. Add SQLAlchemy models.
6. Add Pydantic schemas.
7. Add CRUD and domain services.
8. Add FastAPI routes.
9. Add tests.
10. Update schema, ER, API, setup, or development documentation as applicable.

Do not start a later domain while the current slice is incomplete or inconsistent.

## Database design rules

- Normalize aggressively and avoid duplicated facts.
- Every campaign-owned record must include an explicit `campaign_id` or inherit an unambiguous campaign boundary through a strongly constrained parent.
- Validate that related records belong to the same campaign.
- Prefer ledgers and effective-dated history over mutable snapshot fields.
- Use append-only tables for important historical changes where practical.
- Never overwrite history merely to represent a correction.
- Use restrictive foreign keys for durable historical records.
- Avoid cascading deletion from campaigns or historically important entities.
- Archive user-facing roots instead of destructively deleting them.
- Use database constraints for invariants that PostgreSQL can enforce reliably.
- Also validate invariants in Pydantic or the service layer so API clients receive useful errors.
- Use UTC for real-world timestamps. Pendragon in-world dates should remain separately represented.
- Use JSONB only for genuinely unstructured extension data, not as a substitute for relational modeling.
- Add indexes for foreign keys and expected timeline, lookup, filtering, and uniqueness access patterns.

Examples of required historical modeling include:

- Glory as a ledger
- Trait and passion changes as history
- Manor and horse ownership as effective-dated ownership records
- Relationships and household membership with start and end dates or events
- Titles, honors, buildings, inheritance, and economic changes as reconstructable records

## Central event model

The `events` table is the chronological backbone of a campaign. Significant domain changes should reference the event that caused or recorded them where appropriate.

Examples include births, deaths, marriages, inheritance, ownership transfers, oaths, battles, tournament victories, trait or passion changes, and glory awards.

Recorded events are historical records. Corrections should append a superseding event using `supersedes_event_id`; do not add ordinary update or delete endpoints for events.

Use `event_links` for role-aware links between events and domain entities when a dedicated relationship is not warranted. Do not rely on polymorphic links where a real foreign key is necessary for integrity.

## Migration rules

- Never create one massive migration for the entire project.
- Name SQL migrations with a zero-padded numeric prefix, such as `005_characters.sql`.
- Each SQL migration must be independently runnable after its predecessors.
- Wrap migrations in transactions unless PostgreSQL prohibits it for a particular operation.
- Make seed scripts idempotent.
- Never edit a migration known to have been deployed; add a new corrective migration.
- Keep the Alembic revision graph aligned with the numbered SQL migration source of truth.
- Test both fresh-database upgrades and upgrades from the preceding revision when database infrastructure is available.
- Supabase Row Level Security policies must be intentional. Do not ship permissive placeholder policies.

## SQLAlchemy and service rules

- Use SQLAlchemy 2.x typed declarative mappings with `Mapped` and `mapped_column`.
- Use async SQLAlchemy sessions throughout request handling.
- Keep HTTP concerns out of models and services.
- Routes should be thin: validate input, call a service, and return the declared response.
- Services own business rules, campaign-boundary validation, transactions, and domain-specific conflicts.
- Do not expose raw SQLAlchemy exceptions through the API.
- Avoid implicit lazy loading during response serialization.
- Prevent N+1 queries with explicit eager-loading strategies where relationships are returned.
- Commit once per logical operation unless a documented workflow requires otherwise.

## API and schema rules

- Place the versioned REST API beneath `/api/v1`.
- Scope campaign-owned resources beneath `/campaigns/{campaign_id}` where practical.
- Provide CRUD endpoints for mutable major entities.
- Historical ledgers and event records should generally support create and read, not destructive mutation.
- Use PATCH for partial updates and exclude unset values in the service layer.
- Return `404` for missing resources and `409` for uniqueness or domain-state conflicts.
- Declare response models for every application endpoint.
- Keep OpenAPI operation names, tags, descriptions, and schemas usable by Custom GPT Actions.
- Prefer bounded pagination for collections that can grow across decades of campaign history.
- Never expose GM-only information through player-facing endpoints or schemas.

## Testing requirements

Every vertical slice should test, as applicable:

- Pydantic validation and boundary cases
- Database constraints and uniqueness
- Cross-campaign isolation
- Service success and failure paths
- API status codes and response shapes
- Historical append-only or supersession behavior
- OpenAPI route presence and forbidden mutation methods
- Migration upgrades against PostgreSQL when a test database is available

SQLite is not an adequate substitute for PostgreSQL-specific integration tests because this project uses PostgreSQL types and behavior.

Before considering a slice complete, run:

```powershell
py -3.12 -m ruff format .
py -3.12 -m ruff check .
py -3.12 -m pytest -q
py -3.12 -m alembic heads
py -3.12 -m compileall -q app migrations tests
```

Do not hide an earlier command failure by chaining commands in a way that returns only the final command's exit status.

## Seed-data rules

Canonical seed targets include Logres, Salisbury, Uther, Roderick, a sample player knight, and a sample manor. Add each item only after its underlying domain schema exists.

Seed data must:

- be idempotent;
- use stable natural identifiers or documented UUIDs where cross-file references require them;
- avoid copyrighted prose or unnecessary setting text;
- remain clearly distinguishable from user campaign data.

## Documentation rules

Keep documentation synchronized with implemented behavior in the same change.

Maintain:

- setup instructions;
- schema documentation and design decisions;
- Mermaid ER diagrams;
- API usage notes, with OpenAPI as the authoritative endpoint reference;
- development and migration guidance.

Document only implemented behavior as current. Clearly label future design as planned.

## Scope and safety

- Preserve unrelated user changes in a dirty worktree.
- Do not commit, push, deploy, reset, or delete data unless explicitly requested.
- Do not run destructive database operations against an unknown or shared database.
- Never print credentials, Supabase keys, database URLs containing passwords, or GM-only campaign content unnecessarily.
- If a live database is unavailable, complete static checks and clearly report which integration checks remain unverified.

## Definition of done

A domain slice is complete only when its schema, migration, ORM mappings, validation models, services, routes, tests, and relevant documentation agree with one another; validation passes; and any unverified PostgreSQL or Supabase behavior is explicitly reported.
