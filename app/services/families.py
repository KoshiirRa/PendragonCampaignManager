from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Character,
    CharacterParentage,
    DiceLog,
    Event,
    Family,
    FamilyHistoryEntry,
    FamilyMembership,
    GloryLedger,
    InheritanceCase,
    InheritanceHeir,
    InheritanceManorTransfer,
    Location,
    Manor,
    ManorTenure,
    Marriage,
    SourceReference,
)
from app.services.campaigns import get_campaign
from app.services.errors import ConflictError, NotFoundError


async def _item(db: AsyncSession, model: type, item_id: UUID, campaign_id: UUID, label: str):
    item = await db.get(model, item_id)
    if item is None or item.campaign_id != campaign_id:
        raise NotFoundError(f"{label} not found")
    return item


async def _commit(db: AsyncSession, item: Any):
    db.add(item)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise ConflictError("Record conflicts with existing campaign history") from exc
    await db.refresh(item)
    return item


async def list_families(db, campaign_id):
    await get_campaign(db, campaign_id)
    return list(
        await db.scalars(
            select(Family)
            .where(Family.campaign_id == campaign_id, Family.archived_at.is_(None))
            .order_by(Family.name)
        )
    )


async def create_family(db, campaign_id, data):
    await get_campaign(db, campaign_id)
    if data.origin_location_id:
        await _item(db, Location, data.origin_location_id, campaign_id, "Origin location")
    values = data.model_dump(exclude={"metadata"})
    return await _commit(db, Family(campaign_id=campaign_id, **values, metadata_=data.metadata))


async def add_membership(db, campaign_id, family_id, data):
    await _item(db, Family, family_id, campaign_id, "Family")
    await _item(db, Character, data.character_id, campaign_id, "Character")
    return await _commit(
        db, FamilyMembership(campaign_id=campaign_id, family_id=family_id, **data.model_dump())
    )


async def add_parentage(db, campaign_id, data):
    await _item(db, Character, data.parent_character_id, campaign_id, "Parent")
    await _item(db, Character, data.child_character_id, campaign_id, "Child")
    frontier = [data.parent_character_id]
    visited = set()
    while frontier:
        current = frontier.pop()
        if current == data.child_character_id:
            raise ConflictError("Parentage would contain a cycle")
        if current in visited:
            continue
        visited.add(current)
        frontier.extend(
            await db.scalars(
                select(CharacterParentage.parent_character_id).where(
                    CharacterParentage.child_character_id == current
                )
            )
        )
    return await _commit(db, CharacterParentage(campaign_id=campaign_id, **data.model_dump()))


async def add_marriage(db, campaign_id, data):
    await _item(db, Character, data.spouse_one_id, campaign_id, "Spouse")
    await _item(db, Character, data.spouse_two_id, campaign_id, "Spouse")
    values = data.model_dump()
    values["spouse_one_id"], values["spouse_two_id"] = sorted(
        (data.spouse_one_id, data.spouse_two_id), key=str
    )
    return await _commit(db, Marriage(campaign_id=campaign_id, **values))


async def create_inheritance_case(db, campaign_id, data):
    await _item(db, Character, data.decedent_character_id, campaign_id, "Decedent")
    return await _commit(db, InheritanceCase(campaign_id=campaign_id, **data.model_dump()))


async def add_heir(db, campaign_id, case_id, data):
    await _item(db, InheritanceCase, case_id, campaign_id, "Inheritance case")
    await _item(db, Character, data.character_id, campaign_id, "Heir")
    return await _commit(
        db,
        InheritanceHeir(campaign_id=campaign_id, inheritance_case_id=case_id, **data.model_dump()),
    )


async def transfer_manor(db, campaign_id, case_id, data):
    await _item(db, InheritanceCase, case_id, campaign_id, "Inheritance case")
    await _item(db, Manor, data.manor_id, campaign_id, "Manor")
    await _item(db, Character, data.beneficiary_character_id, campaign_id, "Beneficiary")
    await _item(db, Event, data.event_id, campaign_id, "Event")
    current = await db.scalar(
        select(ManorTenure).where(
            ManorTenure.manor_id == data.manor_id, ManorTenure.end_year.is_(None)
        )
    )
    if current:
        current.end_year = data.transferred_year
        current.end_event_id = data.event_id
    transfer = InheritanceManorTransfer(
        campaign_id=campaign_id, inheritance_case_id=case_id, **data.model_dump()
    )
    db.add_all(
        [
            transfer,
            ManorTenure(
                campaign_id=campaign_id,
                manor_id=data.manor_id,
                holder_character_id=data.beneficiary_character_id,
                start_event_id=data.event_id,
                start_year=data.transferred_year,
                tenure_type="inheritance",
                terms=data.terms,
            ),
        ]
    )
    return await _commit(db, transfer)


async def create_source(db, campaign_id, data):
    await get_campaign(db, campaign_id)
    return await _commit(db, SourceReference(campaign_id=campaign_id, **data.model_dump()))


async def list_sources(db, campaign_id):
    await get_campaign(db, campaign_id)
    return list(
        await db.scalars(
            select(SourceReference)
            .where(SourceReference.campaign_id == campaign_id)
            .order_by(SourceReference.title)
        )
    )


async def add_history(db, campaign_id, family_id, data):
    await _item(db, Family, family_id, campaign_id, "Family")
    for model, value, label in (
        (Character, data.ancestor_character_id, "Ancestor"),
        (Location, data.realm_location_id, "Realm"),
        (SourceReference, data.source_reference_id, "Source"),
        (DiceLog, data.dice_log_id, "Dice log"),
    ):
        if value:
            await _item(db, model, value, campaign_id, label)
    event = Event(
        campaign_id=campaign_id,
        event_type=f"family_history.{data.entry_type}",
        title=data.title,
        description=data.summary,
        in_game_year=data.start_year,
        visibility="gm_only" if data.scope == "gm_only" else "players",
        metadata_={"family_id": str(family_id)},
    )
    db.add(event)
    await db.flush()
    glory = None
    if data.glory_amount is not None:
        glory = GloryLedger(
            campaign_id=campaign_id,
            character_id=data.ancestor_character_id,
            event_id=event.id,
            awarded_year=data.start_year,
            amount=data.glory_amount,
            category=data.glory_category,
            reason=data.glory_reason or data.title,
            scope=data.scope,
        )
        db.add(glory)
        await db.flush()
    values = data.model_dump(exclude={"metadata", "glory_amount", "glory_category", "glory_reason"})
    entry = FamilyHistoryEntry(
        campaign_id=campaign_id,
        family_id=family_id,
        event_id=event.id,
        glory_ledger_id=glory.id if glory else None,
        **values,
        metadata_=data.metadata,
    )
    return await _commit(db, entry)


async def list_history(db, campaign_id, family_id, before_year=None):
    await _item(db, Family, family_id, campaign_id, "Family")
    query = select(FamilyHistoryEntry).where(FamilyHistoryEntry.family_id == family_id)
    if before_year is not None:
        query = query.where(FamilyHistoryEntry.start_year < before_year)
    return list(
        await db.scalars(
            query.order_by(FamilyHistoryEntry.start_year, FamilyHistoryEntry.created_at)
        )
    )
