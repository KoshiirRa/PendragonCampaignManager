# Pendragon Campaign Database

A PostgreSQL/FastAPI backend designed as durable memory for multi-generational Pendragon 6th Edition campaigns.

## Current scope

The implemented backend covers campaigns, sessions, the central event timeline, dice logs,
characters and historical values, Glory, locations and manors, families and inheritance,
ancestral history, Foundry synchronization, possessions, Winter history, manor economics and
households, squires, and annual player chronicles. Numbered migrations currently run through
`019_secure_public_schema.sql`.

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
Get-ChildItem migrations\*.sql | Sort-Object Name | ForEach-Object {
    psql $env:DATABASE_URL -f $_.FullName
}
psql $env:DATABASE_URL -f seed/001_campaign.sql
uvicorn app.main:app --reload
```

See the [player guide](docs/player-guide.md), [schema documentation](docs/schema.md), the [ER diagram](docs/er-diagram.md), [API notes](docs/api.md), the [Custom GPT setup guide](docs/custom-gpt-setup.md), the [ChatGPT Actions guide](docs/chatgpt-actions.md), the [versioned OpenAPI schema](docs/openapi.json), the [Supabase workflow](docs/supabase.md), the [frontend deployment guide](docs/frontend-deployment.md), and the [development guide](docs/development.md).

## Player chronicle

The [`frontend`](frontend/) directory contains the Cloudflare-hosted, read-only campaign chronicle.
The live Salisbury campaign is available at
[`salisbury.pendragon-chronicle.dwarvenbard.com`](https://salisbury.pendragon-chronicle.dwarvenbard.com).
The hostname slug selects a campaign, and the Worker loads the current player-safe projection from
FastAPI on each request through a server-side proxy. The backend credential is never sent to browser
code. Pushes to `main` that change the frontend or its deployment workflow automatically lint,
build, deploy, and restore the Worker secret binding.

For containerized hosting, secrets, migration jobs, and the deployment pipeline, see the [Google Cloud Run deployment guide](docs/cloud-run.md).

## Security boundary

FastAPI is the sole supported data-access boundary. Supabase's `public` tables have Row-Level
Security enabled without direct Data API policies, and the `anon` and `authenticated` roles have no
table or sequence privileges. Browser clients, Foundry, and Custom GPT Actions must call the
authenticated FastAPI or gateway endpoints; they must never receive database credentials or a
Supabase service-role key.
