from fastapi import FastAPI

from app.api.errors import install_error_handlers
from app.api.routes import campaigns_router, events_router
from app.config import settings

app = FastAPI(
    title="Pendragon Campaign Database",
    description="Persistent multi-generational campaign memory for Pendragon 6th Edition.",
    version="0.1.0",
)
install_error_handlers(app)
app.include_router(campaigns_router, prefix=settings.api_prefix)
app.include_router(events_router, prefix=settings.api_prefix)


@app.get("/health", tags=["operations"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
