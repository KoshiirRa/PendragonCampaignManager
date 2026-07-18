import logging
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    ArmourProfile,
    Character,
    CharacterInventoryLedger,
    CharacterNote,
    CharacterPassion,
    CharacterPassionLedger,
    CharacterSkillLedger,
    CharacterStatLedger,
    CharacterStatusLedger,
    CharacterTraitLedger,
    Event,
    EventLink,
    EventVisibility,
    GloryLedger,
    Horse,
    HorseOwnershipHistory,
    HorseStatLedger,
    InventoryItem,
    KnowledgeScope,
    SkillDefinition,
    TraitDefinition,
    WeaponProfile,
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

logger = logging.getLogger(__name__)


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

    stat_added = 0
    if data.stats is not None:
        latest_stats = await _latest_by_key(
            db,
            CharacterStatLedger,
            CharacterStatLedger.stat_code,
            CharacterStatLedger.character_id == character_id,
        )
        for snapshot in data.stats:
            previous = latest_stats.get(snapshot.code)
            if previous and previous.value == snapshot.value:
                continue
            pending.append(
                CharacterStatLedger(
                    campaign_id=campaign_id,
                    character_id=character_id,
                    stat_code=snapshot.code,
                    effective_year=data.effective_year,
                    value=snapshot.value,
                    reason=reason,
                )
            )
            stat_added += 1

    inventory_created = 0
    inventory_added = 0
    if data.inventory is not None:
        items = list(
            await db.scalars(select(InventoryItem).where(InventoryItem.campaign_id == campaign_id))
        )
        item_by_source = {item.source_key: item for item in items}
        latest_inventory = await _latest_by_key(
            db,
            CharacterInventoryLedger,
            CharacterInventoryLedger.inventory_item_id,
            CharacterInventoryLedger.character_id == character_id,
        )
        incoming_keys = {snapshot.source_key for snapshot in data.inventory}
        for snapshot in data.inventory:
            item = item_by_source.get(snapshot.source_key)
            if item is None:
                item = InventoryItem(
                    campaign_id=campaign_id,
                    source_key=snapshot.source_key,
                    item_type=snapshot.item_type,
                    name=snapshot.name,
                    description=snapshot.description,
                    libra=snapshot.libra,
                    denarii=snapshot.denarii,
                )
                db.add(item)
                await db.flush()
                item_by_source[snapshot.source_key] = item
                inventory_created += 1
                if snapshot.item_type == "weapon":
                    db.add(
                        WeaponProfile(
                            inventory_item_id=item.id,
                            skill=snapshot.skill,
                            damage_formula=snapshot.damage_formula,
                            weapon_range=snapshot.weapon_range,
                            mounted_use=snapshot.mounted_use,
                            melee=snapshot.melee,
                        )
                    )
                elif snapshot.item_type == "armour":
                    db.add(
                        ArmourProfile(
                            inventory_item_id=item.id,
                            armour_points=snapshot.armour_points,
                            material=snapshot.material,
                            is_shield=snapshot.is_shield,
                        )
                    )
            previous = latest_inventory.get(item.id)
            if previous and (previous.quantity, previous.equipped) == (
                snapshot.quantity,
                snapshot.equipped,
            ):
                continue
            pending.append(
                CharacterInventoryLedger(
                    campaign_id=campaign_id,
                    character_id=character_id,
                    inventory_item_id=item.id,
                    effective_year=data.effective_year,
                    quantity=snapshot.quantity,
                    equipped=snapshot.equipped,
                    reason=reason,
                )
            )
            inventory_added += 1
        for item in items:
            previous = latest_inventory.get(item.id)
            if item.source_key not in incoming_keys and previous and previous.quantity > 0:
                pending.append(
                    CharacterInventoryLedger(
                        campaign_id=campaign_id,
                        character_id=character_id,
                        inventory_item_id=item.id,
                        effective_year=data.effective_year,
                        quantity=0,
                        equipped=False,
                        reason="Absent from Foundry VTT inventory snapshot",
                    )
                )
                inventory_added += 1

    horses_created = 0
    horse_added = 0
    ownership_changes = 0
    ownership_pending: list[tuple[HorseOwnershipHistory, str]] = []
    if data.horses is not None:
        horses = list(await db.scalars(select(Horse).where(Horse.campaign_id == campaign_id)))
        horse_by_source = {horse.source_key: horse for horse in horses}
        open_ownerships = list(
            await db.scalars(
                select(HorseOwnershipHistory).where(
                    HorseOwnershipHistory.campaign_id == campaign_id,
                    HorseOwnershipHistory.end_year.is_(None),
                )
            )
        )
        ownership_by_horse = {ownership.horse_id: ownership for ownership in open_ownerships}
        latest_horse_stats = (
            await _latest_by_key(
                db,
                HorseStatLedger,
                HorseStatLedger.horse_id,
                HorseStatLedger.horse_id.in_([horse.id for horse in horses]),
            )
            if horses
            else {}
        )
        incoming_keys = {snapshot.source_key for snapshot in data.horses}
        horse_fields = (
            "siz",
            "dex",
            "str",
            "con",
            "hp",
            "max_hp",
            "move",
            "armour",
            "horse_armour",
            "age",
            "equipped",
        )
        for snapshot in data.horses:
            horse = horse_by_source.get(snapshot.source_key)
            if horse is None:
                horse = Horse(
                    campaign_id=campaign_id,
                    source_key=snapshot.source_key,
                    name=snapshot.name,
                    breed=snapshot.breed,
                    colour=snapshot.colour,
                    personality=snapshot.personality,
                    features=snapshot.features,
                    description=snapshot.description,
                )
                db.add(horse)
                await db.flush()
                horse_by_source[snapshot.source_key] = horse
                horses_created += 1
            ownership = ownership_by_horse.get(horse.id)
            if ownership is None or ownership.character_id != character_id:
                if ownership is not None:
                    ownership.end_year = data.effective_year
                    ownership_pending.append((ownership, "end"))
                    await db.flush()
                new_ownership = HorseOwnershipHistory(
                    campaign_id=campaign_id,
                    horse_id=horse.id,
                    character_id=character_id,
                    start_year=data.effective_year,
                )
                db.add(new_ownership)
                ownership_pending.append((new_ownership, "start"))
                ownership_by_horse[horse.id] = new_ownership
                ownership_changes += 1
            previous = latest_horse_stats.get(horse.id)
            if previous and all(
                getattr(previous, field) == getattr(snapshot, field) for field in horse_fields
            ):
                continue
            pending.append(
                HorseStatLedger(
                    campaign_id=campaign_id,
                    horse_id=horse.id,
                    effective_year=data.effective_year,
                    reason=reason,
                    **{field: getattr(snapshot, field) for field in horse_fields},
                )
            )
            horse_added += 1
        for horse in horses:
            ownership = ownership_by_horse.get(horse.id)
            if (
                horse.source_key not in incoming_keys
                and ownership
                and ownership.character_id == character_id
            ):
                ownership.end_year = data.effective_year
                ownership_pending.append((ownership, "end"))
                ownership_changes += 1

    event = None
    if pending or ownership_pending:
        event = Event(
            campaign_id=campaign_id,
            event_type="foundry_character_sync",
            title=f"Synchronized {character.name} from Foundry VTT",
            description=(
                f"Recorded {trait_added} trait, {skill_added} skill, "
                f"{passion_added} passion, {stat_added} statistic, {inventory_added} inventory, "
                f"{horse_added} horse, and Glory {glory_adjustment:+d} changes."
            ),
            in_game_year=data.effective_year,
            visibility=EventVisibility.PLAYERS,
            metadata_={"source": "foundry_vtt", "foundry_uuid": character.foundry_uuid},
        )
        db.add(event)
        await db.flush()
        db.add(EventLink(event_id=event.id, entity_type="character", entity_id=character_id))
        for ownership, boundary in ownership_pending:
            if boundary == "start":
                ownership.start_event_id = event.id
            else:
                ownership.end_event_id = event.id
        for item in pending:
            item.event_id = event.id
            db.add(item)
    try:
        await db.flush()
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        logger.exception(
            "Foundry snapshot integrity conflict for campaign=%s character=%s",
            campaign_id,
            character_id,
        )
        raise ConflictError("Foundry snapshot conflicts with existing character data") from exc
    return FoundryCharacterSyncResult(
        character_id=character_id,
        event_id=event.id if event else None,
        trait_entries_added=trait_added,
        skill_entries_added=skill_added,
        passions_created=passions_created,
        passion_entries_added=passion_added,
        glory_adjustment=glory_adjustment,
        stat_entries_added=stat_added,
        inventory_items_created=inventory_created,
        inventory_entries_added=inventory_added,
        horses_created=horses_created,
        horse_entries_added=horse_added,
        ownership_changes=ownership_changes,
        changed=bool(pending or ownership_pending),
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
