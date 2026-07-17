from app.api.routes.campaigns import router as campaigns_router
from app.api.routes.characters import router as characters_router
from app.api.routes.events import router as events_router
from app.api.routes.families import router as families_router
from app.api.routes.locations import router as locations_router

__all__ = [
    "campaigns_router",
    "characters_router",
    "events_router",
    "families_router",
    "locations_router",
]
