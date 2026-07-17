from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.dependencies import DB
from app.schemas import DiceLogCreate, DiceLogRead, EventCreate, EventRead
from app.services import events as service

router = APIRouter(prefix="/campaigns/{campaign_id}", tags=["timeline"])


@router.get("/events", response_model=list[EventRead])
async def list_events(
    campaign_id: UUID, db: DB, year: Annotated[int | None, Query(ge=1, le=9999)] = None
):
    return await service.list_events(db, campaign_id, year)


@router.post("/events", response_model=EventRead, status_code=status.HTTP_201_CREATED)
async def create_event(campaign_id: UUID, data: EventCreate, db: DB):
    return await service.create_event(db, campaign_id, data)


@router.post("/dice-logs", response_model=DiceLogRead, status_code=status.HTTP_201_CREATED)
async def create_dice_log(campaign_id: UUID, data: DiceLogCreate, db: DB):
    return await service.create_dice_log(db, campaign_id, data)
