from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Character,
    CharacterNote,
    CharacterPassion,
    CharacterPassionLedger,
    CharacterSkillLedger,
    CharacterStatusLedger,
    CharacterTraitLedger,
    GloryLedger,
    SkillDefinition,
    TraitDefinition,
)
from app.schemas.character import (
    CharacterCreate,
    CharacterNoteCreate,
    CharacterStatusCreate,
    CharacterUpdate,
    GloryCreate,
    PassionCreate,
    PassionLedgerCreate,
    SkillDefinitionCreate,
    SkillLedgerCreate,
    TraitDefinitionCreate,
    TraitLedgerCreate,
)
from app.services.campaigns import get_campaign
from app.services.errors import ConflictError, NotFoundError


async def _campaign_item[T](
    db: AsyncSession, model: type[T], item_id: UUID, campaign_id: UUID, label: str
) -> T:
    item = await db.get(model, item_id)
    if item is None or getattr(item, "campaign_id", None) != campaign_id:
        raise NotFoundError(f"{label} not found")
    return item


async def _commit(db: AsyncSession, item: Any, conflict: str | None = None) -> Any:
    db.add(item)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise ConflictError(conflict or "Record conflicts with existing campaign history") from exc
    await db.refresh(item)
    return item


async def list_characters(
    db: AsyncSession, campaign_id: UUID, kind: str | None = None
) -> list[Character]:
    await get_campaign(db, campaign_id)
    query = select(Character).where(
        Character.campaign_id == campaign_id, Character.archived_at.is_(None)
    )
    if kind:
        query = query.where(Character.kind == kind)
    return list(await db.scalars(query.order_by(Character.name)))


async def get_character(db: AsyncSession, campaign_id: UUID, character_id: UUID) -> Character:
    character = await _campaign_item(db, Character, character_id, campaign_id, "Character")
    if character.archived_at is not None:
        raise NotFoundError("Character not found")
    return character


async def create_character(db: AsyncSession, campaign_id: UUID, data: CharacterCreate) -> Character:
    campaign = await get_campaign(db, campaign_id)
    item = Character(
        campaign_id=campaign_id,
        **data.model_dump(exclude={"metadata"}),
        metadata_=data.metadata,
    )
    db.add(item)
    try:
        await db.flush()
        db.add(
            CharacterStatusLedger(
                campaign_id=campaign_id,
                character_id=item.id,
                status=data.status,
                effective_year=data.birth_year or campaign.current_year,
                reason="Initial character status",
            )
        )
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise ConflictError("Character identity or Foundry UUID already exists") from exc
    await db.refresh(item)
    return item


async def update_character(
    db: AsyncSession, campaign_id: UUID, character_id: UUID, data: CharacterUpdate
) -> Character:
    item = await get_character(db, campaign_id, character_id)
    for field, value in data.model_dump(exclude_unset=True, exclude={"metadata"}).items():
        setattr(item, field, value)
    if "metadata" in data.model_fields_set:
        item.metadata_ = data.metadata or {}
    if item.kind == "player_knight" and not item.player_name:
        raise ConflictError("player_name is required for a player knight")
    return await _commit(db, item, "Character update conflicts with an existing identity")


async def archive_character(db: AsyncSession, campaign_id: UUID, character_id: UUID) -> None:
    item = await get_character(db, campaign_id, character_id)
    item.archived_at = datetime.now(UTC)
    await db.commit()


async def add_status(
    db: AsyncSession, campaign_id: UUID, character_id: UUID, data: CharacterStatusCreate
) -> CharacterStatusLedger:
    await get_character(db, campaign_id, character_id)
    return await _commit(
        db,
        CharacterStatusLedger(
            campaign_id=campaign_id, character_id=character_id, **data.model_dump()
        ),
    )


async def list_status_history(
    db: AsyncSession, campaign_id: UUID, character_id: UUID
) -> list[CharacterStatusLedger]:
    await get_character(db, campaign_id, character_id)
    return list(
        await db.scalars(
            select(CharacterStatusLedger)
            .where(CharacterStatusLedger.character_id == character_id)
            .order_by(
                CharacterStatusLedger.effective_year,
                CharacterStatusLedger.sequence,
                CharacterStatusLedger.recorded_at,
            )
        )
    )


async def add_note(
    db: AsyncSession, campaign_id: UUID, character_id: UUID, data: CharacterNoteCreate
) -> CharacterNote:
    await get_character(db, campaign_id, character_id)
    return await _commit(
        db, CharacterNote(campaign_id=campaign_id, character_id=character_id, **data.model_dump())
    )


async def list_notes(
    db: AsyncSession, campaign_id: UUID, character_id: UUID, include_gm: bool
) -> list[CharacterNote]:
    await get_character(db, campaign_id, character_id)
    query = select(CharacterNote).where(CharacterNote.character_id == character_id)
    if not include_gm:
        query = query.where(CharacterNote.scope != "gm_only")
    return list(await db.scalars(query.order_by(CharacterNote.recorded_at)))


async def create_trait_definition(
    db: AsyncSession, campaign_id: UUID, data: TraitDefinitionCreate
) -> TraitDefinition:
    await get_campaign(db, campaign_id)
    return await _commit(
        db,
        TraitDefinition(campaign_id=campaign_id, **data.model_dump()),
        "Trait definition already exists",
    )


async def list_trait_definitions(db: AsyncSession, campaign_id: UUID) -> list[TraitDefinition]:
    await get_campaign(db, campaign_id)
    return list(
        await db.scalars(
            select(TraitDefinition)
            .where(TraitDefinition.campaign_id == campaign_id)
            .order_by(TraitDefinition.name)
        )
    )


async def add_trait_entry(
    db: AsyncSession, campaign_id: UUID, character_id: UUID, data: TraitLedgerCreate
) -> CharacterTraitLedger:
    await get_character(db, campaign_id, character_id)
    await _campaign_item(
        db, TraitDefinition, data.trait_definition_id, campaign_id, "Trait definition"
    )
    return await _commit(
        db,
        CharacterTraitLedger(
            campaign_id=campaign_id, character_id=character_id, **data.model_dump()
        ),
    )


async def create_skill_definition(
    db: AsyncSession, campaign_id: UUID, data: SkillDefinitionCreate
) -> SkillDefinition:
    await get_campaign(db, campaign_id)
    return await _commit(
        db,
        SkillDefinition(campaign_id=campaign_id, **data.model_dump()),
        "Skill definition already exists",
    )


async def list_skill_definitions(db: AsyncSession, campaign_id: UUID) -> list[SkillDefinition]:
    await get_campaign(db, campaign_id)
    return list(
        await db.scalars(
            select(SkillDefinition)
            .where(SkillDefinition.campaign_id == campaign_id)
            .order_by(SkillDefinition.name)
        )
    )


async def add_skill_entry(
    db: AsyncSession, campaign_id: UUID, character_id: UUID, data: SkillLedgerCreate
) -> CharacterSkillLedger:
    await get_character(db, campaign_id, character_id)
    await _campaign_item(
        db, SkillDefinition, data.skill_definition_id, campaign_id, "Skill definition"
    )
    return await _commit(
        db,
        CharacterSkillLedger(
            campaign_id=campaign_id, character_id=character_id, **data.model_dump()
        ),
    )


async def create_passion(
    db: AsyncSession, campaign_id: UUID, character_id: UUID, data: PassionCreate
) -> CharacterPassion:
    await get_character(db, campaign_id, character_id)
    if data.related_character_id:
        await get_character(db, campaign_id, data.related_character_id)
    return await _commit(
        db,
        CharacterPassion(campaign_id=campaign_id, character_id=character_id, **data.model_dump()),
    )


async def add_passion_entry(
    db: AsyncSession,
    campaign_id: UUID,
    character_id: UUID,
    passion_id: UUID,
    data: PassionLedgerCreate,
) -> CharacterPassionLedger:
    await get_character(db, campaign_id, character_id)
    passion = await _campaign_item(db, CharacterPassion, passion_id, campaign_id, "Passion")
    if passion.character_id != character_id:
        raise NotFoundError("Passion not found")
    return await _commit(
        db,
        CharacterPassionLedger(campaign_id=campaign_id, passion_id=passion_id, **data.model_dump()),
    )


async def add_glory(
    db: AsyncSession, campaign_id: UUID, character_id: UUID, data: GloryCreate
) -> GloryLedger:
    await get_character(db, campaign_id, character_id)
    return await _commit(
        db, GloryLedger(campaign_id=campaign_id, character_id=character_id, **data.model_dump())
    )


async def glory_summary(
    db: AsyncSession, campaign_id: UUID, character_id: UUID, include_gm: bool
) -> tuple[list[GloryLedger], int]:
    await get_character(db, campaign_id, character_id)
    condition = [GloryLedger.character_id == character_id]
    if not include_gm:
        condition.append(GloryLedger.scope != "gm_only")
    query = select(GloryLedger).where(*condition)
    entries = list(
        await db.scalars(
            query.order_by(GloryLedger.awarded_year, GloryLedger.sequence, GloryLedger.recorded_at)
        )
    )
    total = await db.scalar(
        select(func.coalesce(func.sum(GloryLedger.amount), 0)).where(*condition)
    )
    return entries, int(total or 0)
