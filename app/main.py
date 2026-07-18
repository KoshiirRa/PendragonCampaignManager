from contextlib import asynccontextmanager

from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.errors import UnhandledErrorMiddleware, install_error_handlers
from app.api.routes import (
    campaigns_router,
    characters_router,
    events_router,
    families_router,
    locations_router,
    winter_router,
)
from app.config import settings
from app.database import engine
from app.openapi import (
    build_gpt_dynasty_openapi,
    build_gpt_play_openapi,
    build_gpt_winter_openapi,
    build_openapi,
)
from app.security import APIKeyMiddleware


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(
    title="Pendragon Campaign Database",
    description="Persistent multi-generational campaign memory for Pendragon 6th Edition.",
    version="0.1.0",
    lifespan=lifespan,
    servers=[{"url": settings.public_base_url, "description": "Pendragon Campaign API"}],
    generate_unique_id_function=lambda route: route.name,
)
app.add_middleware(APIKeyMiddleware, api_key=settings.api_key)
app.add_middleware(UnhandledErrorMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key"],
)
install_error_handlers(app)
app.include_router(campaigns_router, prefix=settings.api_prefix)
app.include_router(events_router, prefix=settings.api_prefix)
app.include_router(characters_router, prefix=settings.api_prefix)
app.include_router(locations_router, prefix=settings.api_prefix)
app.include_router(families_router, prefix=settings.api_prefix)
app.include_router(winter_router, prefix=settings.api_prefix)


@app.get("/health", tags=["operations"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready", tags=["operations"], response_model=None)
async def ready() -> Response:
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unavailable"},
        )
    return JSONResponse(content={"status": "ready"})


@app.get("/privacy", include_in_schema=False, response_class=HTMLResponse)
async def privacy_policy() -> HTMLResponse:
    return HTMLResponse(
        content="""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Privacy Policy - Pendragon Campaign Manager</title>
  <style>
    body { max-width: 48rem; margin: 3rem auto; padding: 0 1.25rem; color: #241d18;
      background: #fbf8f1; font: 17px/1.65 Georgia, serif; }
    h1, h2 { line-height: 1.2; color: #4b251d; }
    a { color: #70402f; }
    .effective { color: #655b52; }
  </style>
</head>
<body>
  <main>
    <h1>Pendragon Campaign Manager Privacy Policy</h1>
    <p class="effective"><strong>Effective date:</strong> July 18, 2026</p>
    <p>This policy explains how the privately operated Pendragon Campaign Manager API
    processes information when it is used through a Custom GPT Action or another authorized
    client.</p>

    <h2>Information processed</h2>
    <p>The service processes the campaign information submitted by an authorized user. This may
    include fictional character, family, event, dice-roll, property, and campaign-note data. Users
    should not submit real-world sensitive personal information. The hosting providers may also
    process ordinary technical data such as IP addresses, request times, response codes, and user
    agent information in security and operational logs.</p>

    <h2>How information is used</h2>
    <p>Information is used only to provide persistent campaign memory, return requested campaign
    records, generate player-safe campaign projections and chronicles, secure the service,
    diagnose failures, and maintain reliable operation. It is not sold or used for advertising.</p>

    <h2>Service providers and disclosure</h2>
    <p>The API runs on Google Cloud, and campaign records are stored in Supabase. Those providers
    process information as needed to host, secure, monitor, and back up the service under their
    own terms and privacy commitments. Information may also be disclosed when required by law or
    when reasonably necessary to protect the service, its users, or others.</p>

    <h2>Retention</h2>
    <p>Campaign history is intentionally durable and may be retained until the campaign owner
    requests archival or deletion, subject to technical, legal, security, and backup-retention
    requirements. Operational logs are retained according to the configured policies of the
    hosting providers.</p>

    <h2>Security and access</h2>
    <p>Application access is protected by an API key stored in the Custom GPT Action authentication
    settings. Credentials are not included in the public OpenAPI schemas. No method of storage or
    transmission is completely secure, and users should avoid entering real-world confidential or
    sensitive personal data into campaign records.</p>

    <h2>User choices</h2>
    <p>An authorized campaign owner may request access, correction through the campaign's
    historical correction mechanisms, archival, or deletion where appropriate. Some append-only
    historical records are preserved to maintain campaign integrity unless the campaign itself is
    removed.</p>

    <h2>Children</h2>
    <p>This service is not directed to children under 13 and is not intended to collect their
    personal information.</p>

    <h2>Changes and contact</h2>
    <p>This policy may be updated as the service changes. The effective date above will be revised
    when material changes are published. Questions or privacy requests may be submitted through
    the project's
    <a href="https://github.com/KoshiirRa/PendragonCampaignManager/issues">GitHub issue tracker</a>.
    Do not include API keys or sensitive campaign content in a public issue.</p>
  </main>
</body>
</html>"""
    )


@app.get("/openapi-gpt-play.json", include_in_schema=False)
async def openapi_gpt_play() -> JSONResponse:
    return JSONResponse(content=build_gpt_play_openapi(app))


@app.get("/openapi-gpt-dynasty.json", include_in_schema=False)
async def openapi_gpt_dynasty() -> JSONResponse:
    return JSONResponse(content=build_gpt_dynasty_openapi(app))


@app.get("/openapi-gpt-winter.json", include_in_schema=False)
async def openapi_gpt_winter() -> JSONResponse:
    return JSONResponse(content=build_gpt_winter_openapi(app))


app.openapi = lambda: build_openapi(app)
