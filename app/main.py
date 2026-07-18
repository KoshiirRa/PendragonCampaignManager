from contextlib import asynccontextmanager

from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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
from app.openapi import build_openapi
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


app.openapi = lambda: build_openapi(app)
