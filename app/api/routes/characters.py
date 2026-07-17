from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.dependencies import DB
from app.schemas.character import (
    CharacterCreate,
    CharacterNoteCreate,
    CharacterNoteRead,
    CharacterRead,
    CharacterStatusCreate,
    CharacterStatusRead,
    CharacterUpdate,
    FoundryCharacterSnapshot,
    FoundryCharacterSyncResult,
    GloryCreate,
    GloryRead,
    GlorySummary,
    PassionCreate,
    PassionLedgerCreate,
    PassionLedgerRead,
    PassionRead,
    SkillDefinitionCreate,
    SkillDefinitionRead,
    SkillLedgerCreate,
    SkillLedgerRead,
    TraitDefinitionCreate,
    TraitDefinitionRead,
    TraitLedgerCreate,
    TraitLedgerRead,
)
from app.services import characters as service

router = APIRouter(prefix="/campaigns/{campaign_id}", tags=["characters"])


@router.get("/characters", response_model=list[CharacterRead])
async def list_characters(
    campaign_id: UUID,
    db: DB,
    kind: Annotated[str | None, Query(pattern="^(player_knight|npc)$")] = None,
):
    return await service.list_characters(db, campaign_id, kind)


@router.post("/characters", response_model=CharacterRead, status_code=status.HTTP_201_CREATED)
async def create_character(campaign_id: UUID, data: CharacterCreate, db: DB):
    return await service.create_character(db, campaign_id, data)


@router.get("/characters/{character_id}", response_model=CharacterRead)
async def get_character(campaign_id: UUID, character_id: UUID, db: DB):
    return await service.get_character(db, campaign_id, character_id)


@router.patch("/characters/{character_id}", response_model=CharacterRead)
async def update_character(campaign_id: UUID, character_id: UUID, data: CharacterUpdate, db: DB):
    return await service.update_character(db, campaign_id, character_id, data)


@router.delete("/characters/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
async def archive_character(campaign_id: UUID, character_id: UUID, db: DB):
    await service.archive_character(db, campaign_id, character_id)


@router.get("/characters/{character_id}/status-ledger", response_model=list[CharacterStatusRead])
async def list_status_history(campaign_id: UUID, character_id: UUID, db: DB):
    return await service.list_status_history(db, campaign_id, character_id)


@router.post(
    "/characters/{character_id}/status-ledger",
    response_model=CharacterStatusRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_status(campaign_id: UUID, character_id: UUID, data: CharacterStatusCreate, db: DB):
    return await service.add_status(db, campaign_id, character_id, data)


@router.get("/characters/{character_id}/notes", response_model=list[CharacterNoteRead])
async def list_notes(campaign_id: UUID, character_id: UUID, db: DB, include_gm: bool = False):
    return await service.list_notes(db, campaign_id, character_id, include_gm)


@router.post(
    "/characters/{character_id}/notes",
    response_model=CharacterNoteRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_note(campaign_id: UUID, character_id: UUID, data: CharacterNoteCreate, db: DB):
    return await service.add_note(db, campaign_id, character_id, data)


@router.get("/trait-definitions", response_model=list[TraitDefinitionRead])
async def list_trait_definitions(campaign_id: UUID, db: DB):
    return await service.list_trait_definitions(db, campaign_id)


@router.post(
    "/trait-definitions",
    response_model=TraitDefinitionRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_trait_definition(campaign_id: UUID, data: TraitDefinitionCreate, db: DB):
    return await service.create_trait_definition(db, campaign_id, data)


@router.post(
    "/characters/{character_id}/trait-ledger",
    response_model=TraitLedgerRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_trait_entry(campaign_id: UUID, character_id: UUID, data: TraitLedgerCreate, db: DB):
    return await service.add_trait_entry(db, campaign_id, character_id, data)


@router.get("/skill-definitions", response_model=list[SkillDefinitionRead])
async def list_skill_definitions(campaign_id: UUID, db: DB):
    return await service.list_skill_definitions(db, campaign_id)


@router.post(
    "/skill-definitions",
    response_model=SkillDefinitionRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_skill_definition(campaign_id: UUID, data: SkillDefinitionCreate, db: DB):
    return await service.create_skill_definition(db, campaign_id, data)


@router.post(
    "/characters/{character_id}/skill-ledger",
    response_model=SkillLedgerRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_skill_entry(campaign_id: UUID, character_id: UUID, data: SkillLedgerCreate, db: DB):
    return await service.add_skill_entry(db, campaign_id, character_id, data)


@router.post(
    "/characters/{character_id}/passions",
    response_model=PassionRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_passion(campaign_id: UUID, character_id: UUID, data: PassionCreate, db: DB):
    return await service.create_passion(db, campaign_id, character_id, data)


@router.post(
    "/characters/{character_id}/passions/{passion_id}/ledger",
    response_model=PassionLedgerRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_passion_entry(
    campaign_id: UUID,
    character_id: UUID,
    passion_id: UUID,
    data: PassionLedgerCreate,
    db: DB,
):
    return await service.add_passion_entry(db, campaign_id, character_id, passion_id, data)


@router.get("/characters/{character_id}/glory", response_model=GlorySummary)
async def glory_summary(campaign_id: UUID, character_id: UUID, db: DB, include_gm: bool = False):
    entries, total = await service.glory_summary(db, campaign_id, character_id, include_gm)
    return GlorySummary(character_id=character_id, total=total, entries=entries)


@router.post(
    "/characters/{character_id}/glory",
    response_model=GloryRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_glory(campaign_id: UUID, character_id: UUID, data: GloryCreate, db: DB):
    return await service.add_glory(db, campaign_id, character_id, data)


@router.post(
    "/characters/{character_id}/foundry-snapshot",
    response_model=FoundryCharacterSyncResult,
    summary="Synchronize a Foundry VTT character snapshot",
    description=(
        "Append only trait, skill, passion, and Glory changes from Foundry VTT. "
        "Submitting an unchanged snapshot creates no new historical rows."
    ),
)
async def sync_foundry_snapshot(
    campaign_id: UUID,
    character_id: UUID,
    data: FoundryCharacterSnapshot,
    db: DB,
):
    return await service.sync_foundry_snapshot(db, campaign_id, character_id, data)
