from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CampaignSession, DiceLog, Event
from app.schemas import DiceLogCreate, EventCreate
from app.services.campaigns import get_campaign
from app.services.errors import ConflictError


async def _validate_campaign_reference(
    db: AsyncSession, campaign_id: UUID, session_id: UUID | None
) -> None:
    await get_campaign(db, campaign_id)
    if session_id is not None:
        session = await db.get(CampaignSession, session_id)
        if session is None or session.campaign_id != campaign_id:
            raise ConflictError("session_id does not belong to this campaign")


async def list_events(db: AsyncSession, campaign_id: UUID, year: int | None = None) -> list[Event]:
    await get_campaign(db, campaign_id)
    query = select(Event).where(Event.campaign_id == campaign_id)
    if year is not None:
        query = query.where(Event.in_game_year == year)
    rows = await db.scalars(query.order_by(Event.in_game_year, Event.sequence, Event.recorded_at))
    return list(rows)


async def create_event(db: AsyncSession, campaign_id: UUID, data: EventCreate) -> Event:
    await _validate_campaign_reference(db, campaign_id, data.session_id)
    if data.supersedes_event_id:
        prior = await db.get(Event, data.supersedes_event_id)
        if prior is None or prior.campaign_id != campaign_id:
            raise ConflictError("supersedes_event_id does not belong to this campaign")
    item = Event(
        campaign_id=campaign_id,
        **data.model_dump(exclude={"metadata"}),
        metadata_=data.metadata,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def create_dice_log(db: AsyncSession, campaign_id: UUID, data: DiceLogCreate) -> DiceLog:
    await _validate_campaign_reference(db, campaign_id, data.session_id)
    if data.event_id:
        event = await db.get(Event, data.event_id)
        if event is None or event.campaign_id != campaign_id:
            raise ConflictError("event_id does not belong to this campaign")
    item = DiceLog(
        campaign_id=campaign_id,
        **data.model_dump(exclude={"metadata"}),
        metadata_=data.metadata,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item
