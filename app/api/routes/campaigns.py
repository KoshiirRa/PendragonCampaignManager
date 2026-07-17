from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, Response, status

from app.api.dependencies import DB
from app.schemas import (
    CampaignCreate,
    CampaignRead,
    CampaignUpdate,
    SessionCreate,
    SessionRead,
    SessionUpdate,
)
from app.services import campaigns as service

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.get("", response_model=list[CampaignRead])
async def list_campaigns(
    db: DB,
    response: Response,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    items, total = await service.list_campaigns(db, limit, offset)
    response.headers["X-Total-Count"] = str(total)
    return items


@router.post("", response_model=CampaignRead, status_code=status.HTTP_201_CREATED)
async def create_campaign(data: CampaignCreate, db: DB):
    return await service.create_campaign(db, data)


@router.get("/{campaign_id}", response_model=CampaignRead)
async def get_campaign(campaign_id: UUID, db: DB):
    return await service.get_campaign(db, campaign_id)


@router.patch("/{campaign_id}", response_model=CampaignRead)
async def update_campaign(campaign_id: UUID, data: CampaignUpdate, db: DB):
    return await service.update_campaign(db, campaign_id, data)


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def archive_campaign(campaign_id: UUID, db: DB):
    await service.archive_campaign(db, campaign_id)


@router.get("/{campaign_id}/sessions", response_model=list[SessionRead])
async def list_sessions(campaign_id: UUID, db: DB):
    return await service.list_sessions(db, campaign_id)


@router.post(
    "/{campaign_id}/sessions", response_model=SessionRead, status_code=status.HTTP_201_CREATED
)
async def create_session(campaign_id: UUID, data: SessionCreate, db: DB):
    return await service.create_session(db, campaign_id, data)


@router.patch("/{campaign_id}/sessions/{session_id}", response_model=SessionRead)
async def update_session(campaign_id: UUID, session_id: UUID, data: SessionUpdate, db: DB):
    return await service.update_session(db, campaign_id, session_id, data)
