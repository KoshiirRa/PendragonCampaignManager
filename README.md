# Pendragon Campaign Database

A PostgreSQL/FastAPI backend designed as durable memory for multi-generational Pendragon 6th Edition campaigns.

## Current scope

This first completed vertical slice implements campaigns, play sessions, the central historical event timeline, event/entity links, and dice logs. Character, location, family, and other domains will be added in subsequent internally consistent slices.

## Setup

Requirements: Python 3.12 and PostgreSQL 15+ (a local Supabase stack is suitable).

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
Copy-Item .env.example .env
```

Apply each SQL migration in numeric order using the Supabase SQL editor or `psql`, then optionally apply seed data:

```powershell
psql $env:DATABASE_URL -f migrations/001_extensions.sql
psql $env:DATABASE_URL -f migrations/002_campaign.sql
psql $env:DATABASE_URL -f migrations/003_events.sql
psql $env:DATABASE_URL -f migrations/004_dice_logs.sql
psql $env:DATABASE_URL -f seed/001_campaign.sql
uvicorn app.main:app --reload
```

See the [player guide](docs/player-guide.md), [schema documentation](docs/schema.md), the [ER diagram](docs/er-diagram.md), [API notes](docs/api.md), the [Custom GPT setup guide](docs/custom-gpt-setup.md), the [ChatGPT Actions guide](docs/chatgpt-actions.md), the [versioned OpenAPI schema](docs/openapi.json), the [Supabase workflow](docs/supabase.md), and the [development guide](docs/development.md).

For containerized hosting, secrets, migration jobs, and the deployment pipeline, see the [Google Cloud Run deployment guide](docs/cloud-run.md).
