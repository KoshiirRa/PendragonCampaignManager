from uuid import UUID

from fastapi import APIRouter, status

from app.api.dependencies import DB
from app.schemas.winter import (
    CharacterHistoryRead,
    CharacterWoundRead,
    WinterParticipantRead,
    WinterPhaseCreate,
    WinterPhaseRead,
)
from app.services import winter as service

router = APIRouter(prefix="/campaigns/{campaign_id}", tags=["winter-phase"])


@router.get("/winter-phases", response_model=list[WinterPhaseRead])
async def list_winter_phases(campaign_id: UUID, db: DB):
    return await service.list_phases(db, campaign_id)


@router.post("/winter-phases", response_model=WinterPhaseRead, status_code=status.HTTP_201_CREATED)
async def create_winter_phase(campaign_id: UUID, data: WinterPhaseCreate, db: DB):
    return await service.create_phase(db, campaign_id, data)


@router.get("/winter-phases/{phase_id}/participants", response_model=list[WinterParticipantRead])
async def list_winter_participants(campaign_id: UUID, phase_id: UUID, db: DB):
    return await service.list_participants(db, campaign_id, phase_id)


@router.get("/characters/{character_id}/history", response_model=list[CharacterHistoryRead])
async def list_character_history(campaign_id: UUID, character_id: UUID, db: DB):
    return await service.list_character_history(db, campaign_id, character_id)


@router.get("/characters/{character_id}/wounds", response_model=list[CharacterWoundRead])
async def list_character_wounds(campaign_id: UUID, character_id: UUID, db: DB):
    return await service.list_character_wounds(db, campaign_id, character_id)
