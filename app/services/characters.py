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
    Event,
    EventLink,
    GloryLedger,
    KnowledgeScope,
    SkillDefinition,
    TraitDefinition,
)
from app.schemas.character import (
    CharacterCreate,
    CharacterNoteCreate,
    CharacterStatusCreate,
    CharacterUpdate,
    FoundryCharacterSnapshot,
    FoundryCharacterSyncResult,
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


async def sync_foundry_snapshot(
    db: AsyncSession,
    campaign_id: UUID,
    character_id: UUID,
    data: FoundryCharacterSnapshot,
) -> FoundryCharacterSyncResult:
    character = await get_character(db, campaign_id, character_id)
    reason = "Foundry VTT character synchronization"
    pending: list[Any] = []

    trait_definitions = list(
        await db.scalars(select(TraitDefinition).where(TraitDefinition.campaign_id == campaign_id))
    )
    trait_by_source = {item.source_key: item for item in trait_definitions if item.source_key}
    trait_by_name = {item.name.casefold(): item for item in trait_definitions}
    latest_traits = await _latest_by_key(
        db,
        CharacterTraitLedger,
        CharacterTraitLedger.trait_definition_id,
        CharacterTraitLedger.character_id == character_id,
    )
    trait_added = 0
    for snapshot in data.traits:
        definition = trait_by_source.get(snapshot.source_key) or trait_by_name.get(
            snapshot.name.casefold()
        )
        if definition is None:
            definition = TraitDefinition(
                campaign_id=campaign_id,
                source_key=snapshot.source_key,
                name=snapshot.name,
                opposed_name=snapshot.opposed_name,
            )
            db.add(definition)
            await db.flush()
            trait_by_source[snapshot.source_key] = definition
        elif definition.source_key is None:
            definition.source_key = snapshot.source_key
        previous = latest_traits.get(definition.id)
        if previous and (previous.trait_value, previous.opposed_value) == (
            snapshot.value,
            snapshot.opposed_value,
        ):
            continue
        pending.append(
            CharacterTraitLedger(
                campaign_id=campaign_id,
                character_id=character_id,
                trait_definition_id=definition.id,
                effective_year=data.effective_year,
                trait_value=snapshot.value,
                opposed_value=snapshot.opposed_value,
                reason=reason,
            )
        )
        trait_added += 1

    skill_definitions = list(
        await db.scalars(select(SkillDefinition).where(SkillDefinition.campaign_id == campaign_id))
    )
    skill_by_source = {item.source_key: item for item in skill_definitions if item.source_key}
    skill_by_name = {item.name.casefold(): item for item in skill_definitions}
    latest_skills = await _latest_by_key(
        db,
        CharacterSkillLedger,
        CharacterSkillLedger.skill_definition_id,
        CharacterSkillLedger.character_id == character_id,
    )
    skill_added = 0
    for snapshot in data.skills:
        definition = skill_by_source.get(snapshot.source_key) or skill_by_name.get(
            snapshot.name.casefold()
        )
        if definition is None:
            definition = SkillDefinition(
                campaign_id=campaign_id,
                source_key=snapshot.source_key,
                name=snapshot.name,
                category=snapshot.category,
            )
            db.add(definition)
            await db.flush()
            skill_by_source[snapshot.source_key] = definition
        elif definition.source_key is None:
            definition.source_key = snapshot.source_key
        previous = latest_skills.get(definition.id)
        if previous and previous.value == snapshot.value:
            continue
        pending.append(
            CharacterSkillLedger(
                campaign_id=campaign_id,
                character_id=character_id,
                skill_definition_id=definition.id,
                effective_year=data.effective_year,
                value=snapshot.value,
                reason=reason,
            )
        )
        skill_added += 1

    passions = list(
        await db.scalars(
            select(CharacterPassion).where(CharacterPassion.character_id == character_id)
        )
    )
    passion_by_source = {item.source_key: item for item in passions if item.source_key}
    latest_passions = (
        await _latest_by_key(
            db,
            CharacterPassionLedger,
            CharacterPassionLedger.passion_id,
            CharacterPassionLedger.passion_id.in_([item.id for item in passions]),
        )
        if passions
        else {}
    )
    passions_created = 0
    passion_added = 0
    for snapshot in data.passions:
        passion = passion_by_source.get(snapshot.source_key)
        if passion is None:
            passion = CharacterPassion(
                campaign_id=campaign_id,
                character_id=character_id,
                source_key=snapshot.source_key,
                name=snapshot.name,
                subject_text=snapshot.subject_text,
                scope=KnowledgeScope.PLAYERS,
                started_year=data.effective_year,
            )
            db.add(passion)
            await db.flush()
            passion_by_source[snapshot.source_key] = passion
            passions_created += 1
        previous = latest_passions.get(passion.id)
        if previous and previous.value == snapshot.value:
            continue
        pending.append(
            CharacterPassionLedger(
                campaign_id=campaign_id,
                passion_id=passion.id,
                effective_year=data.effective_year,
                value=snapshot.value,
                reason=reason,
            )
        )
        passion_added += 1

    current_glory = int(
        await db.scalar(
            select(func.coalesce(func.sum(GloryLedger.amount), 0)).where(
                GloryLedger.character_id == character_id
            )
        )
        or 0
    )
    glory_adjustment = data.glory_total - current_glory
    if glory_adjustment:
        pending.append(
            GloryLedger(
                campaign_id=campaign_id,
                character_id=character_id,
                awarded_year=data.effective_year,
                amount=glory_adjustment,
                category="foundry_sync",
                reason="Foundry VTT total Glory reconciliation",
                scope=KnowledgeScope.PLAYERS,
            )
        )

    event = None
    if pending:
        event = Event(
            campaign_id=campaign_id,
            event_type="foundry_character_sync",
            title=f"Synchronized {character.name} from Foundry VTT",
            description=(
                f"Recorded {trait_added} trait, {skill_added} skill, "
                f"{passion_added} passion, and Glory {glory_adjustment:+d} changes."
            ),
            in_game_year=data.effective_year,
            visibility="players",
            metadata_={"source": "foundry_vtt", "foundry_uuid": character.foundry_uuid},
        )
        db.add(event)
        db.add(EventLink(event_id=event.id, entity_type="character", entity_id=character_id))
        for item in pending:
            item.event_id = event.id
            db.add(item)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise ConflictError("Foundry snapshot conflicts with existing character data") from exc
    return FoundryCharacterSyncResult(
        character_id=character_id,
        event_id=event.id if event else None,
        trait_entries_added=trait_added,
        skill_entries_added=skill_added,
        passions_created=passions_created,
        passion_entries_added=passion_added,
        glory_adjustment=glory_adjustment,
        changed=bool(pending),
    )


async def _latest_by_key(db: AsyncSession, model: type[Any], key: Any, condition: Any) -> dict:
    rows = list(
        await db.scalars(
            select(model)
            .where(condition)
            .order_by(
                key,
                model.effective_year.desc(),
                model.sequence.desc(),
                model.recorded_at.desc(),
            )
        )
    )
    latest = {}
    for row in rows:
        latest.setdefault(getattr(row, key.key), row)
    return latest
