from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Character,
    Location,
    Manor,
    ManorImprovement,
    ManorImprovementLedger,
    ManorTenure,
)
from app.schemas.location import (
    LocationCreate,
    LocationUpdate,
    ManorCreate,
    ManorImprovementCreate,
    ManorImprovementLedgerCreate,
    ManorTenureCreate,
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


async def list_locations(
    db: AsyncSession, campaign_id: UUID, kind: str | None = None
) -> list[Location]:
    await get_campaign(db, campaign_id)
    query = select(Location).where(
        Location.campaign_id == campaign_id, Location.archived_at.is_(None)
    )
    if kind:
        query = query.where(Location.kind == kind)
    return list(await db.scalars(query.order_by(Location.name)))


async def get_location(db: AsyncSession, campaign_id: UUID, location_id: UUID) -> Location:
    item = await _campaign_item(db, Location, location_id, campaign_id, "Location")
    if item.archived_at is not None:
        raise NotFoundError("Location not found")
    return item


async def _validate_parent(
    db: AsyncSession, campaign_id: UUID, parent_id: UUID | None, own_id: UUID | None = None
) -> None:
    if parent_id is None:
        return
    if parent_id == own_id:
        raise ConflictError("A location cannot be its own parent")
    parent = await get_location(db, campaign_id, parent_id)
    visited = {parent.id}
    while parent.parent_location_id is not None:
        if parent.parent_location_id == own_id:
            raise ConflictError("Location hierarchy would contain a cycle")
        if parent.parent_location_id in visited:
            raise ConflictError("Existing location hierarchy contains a cycle")
        visited.add(parent.parent_location_id)
        parent = await get_location(db, campaign_id, parent.parent_location_id)


async def create_location(db: AsyncSession, campaign_id: UUID, data: LocationCreate) -> Location:
    await get_campaign(db, campaign_id)
    await _validate_parent(db, campaign_id, data.parent_location_id)
    return await _commit(
        db,
        Location(
            campaign_id=campaign_id,
            **data.model_dump(exclude={"metadata"}),
            metadata_=data.metadata,
        ),
    )


async def update_location(
    db: AsyncSession, campaign_id: UUID, location_id: UUID, data: LocationUpdate
) -> Location:
    item = await get_location(db, campaign_id, location_id)
    if "parent_location_id" in data.model_fields_set:
        await _validate_parent(db, campaign_id, data.parent_location_id, location_id)
    for field, value in data.model_dump(exclude_unset=True, exclude={"metadata"}).items():
        setattr(item, field, value)
    if "metadata" in data.model_fields_set:
        item.metadata_ = data.metadata or {}
    return await _commit(db, item)


async def archive_location(db: AsyncSession, campaign_id: UUID, location_id: UUID) -> None:
    item = await get_location(db, campaign_id, location_id)
    item.archived_at = datetime.now(UTC)
    await db.commit()


async def create_manor(db: AsyncSession, campaign_id: UUID, data: ManorCreate) -> Manor:
    await get_campaign(db, campaign_id)
    await _validate_parent(db, campaign_id, data.location.parent_location_id)
    location = Location(
        campaign_id=campaign_id,
        **data.location.model_dump(exclude={"metadata"}),
        metadata_=data.location.metadata,
    )
    db.add(location)
    await db.flush()
    manor = Manor(
        campaign_id=campaign_id,
        location_id=location.id,
        customary_income=data.customary_income,
        acreage=data.acreage,
        notes=data.notes,
    )
    return await _commit(db, manor, "Location already has a manor record")


async def list_manors(db: AsyncSession, campaign_id: UUID) -> list[Manor]:
    await get_campaign(db, campaign_id)
    return list(
        await db.scalars(select(Manor).where(Manor.campaign_id == campaign_id).order_by(Manor.id))
    )


async def add_tenure(
    db: AsyncSession, campaign_id: UUID, manor_id: UUID, data: ManorTenureCreate
) -> ManorTenure:
    await _campaign_item(db, Manor, manor_id, campaign_id, "Manor")
    await _campaign_item(db, Character, data.holder_character_id, campaign_id, "Holder")
    if data.liege_character_id:
        await _campaign_item(db, Character, data.liege_character_id, campaign_id, "Liege")
    return await _commit(
        db,
        ManorTenure(campaign_id=campaign_id, manor_id=manor_id, **data.model_dump()),
        "Manor already has a current holder",
    )


async def add_improvement(
    db: AsyncSession, campaign_id: UUID, manor_id: UUID, data: ManorImprovementCreate
) -> ManorImprovement:
    await _campaign_item(db, Manor, manor_id, campaign_id, "Manor")
    return await _commit(
        db, ManorImprovement(campaign_id=campaign_id, manor_id=manor_id, **data.model_dump())
    )


async def add_improvement_entry(
    db: AsyncSession,
    campaign_id: UUID,
    manor_id: UUID,
    improvement_id: UUID,
    data: ManorImprovementLedgerCreate,
) -> ManorImprovementLedger:
    await _campaign_item(db, Manor, manor_id, campaign_id, "Manor")
    improvement = await _campaign_item(
        db, ManorImprovement, improvement_id, campaign_id, "Improvement"
    )
    if improvement.manor_id != manor_id:
        raise NotFoundError("Improvement not found")
    return await _commit(
        db,
        ManorImprovementLedger(
            campaign_id=campaign_id, improvement_id=improvement_id, **data.model_dump()
        ),
    )
