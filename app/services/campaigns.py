from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Campaign, CampaignSession
from app.schemas import CampaignCreate, CampaignUpdate, SessionCreate, SessionUpdate
from app.services.errors import ConflictError, NotFoundError


async def list_campaigns(db: AsyncSession, limit: int, offset: int) -> tuple[list[Campaign], int]:
    condition = Campaign.archived_at.is_(None)
    rows = await db.scalars(
        select(Campaign).where(condition).order_by(Campaign.name).limit(limit).offset(offset)
    )
    total = await db.scalar(select(func.count()).select_from(Campaign).where(condition))
    return list(rows), total or 0


async def get_campaign(db: AsyncSession, campaign_id: UUID) -> Campaign:
    campaign = await db.get(Campaign, campaign_id)
    if campaign is None or campaign.archived_at is not None:
        raise NotFoundError("Campaign not found")
    return campaign


async def get_campaign_by_slug(db: AsyncSession, slug: str) -> Campaign:
    campaign = await db.scalar(
        select(Campaign).where(Campaign.slug == slug, Campaign.archived_at.is_(None))
    )
    if campaign is None:
        raise NotFoundError("Campaign not found")
    return campaign


async def create_campaign(db: AsyncSession, data: CampaignCreate) -> Campaign:
    campaign = Campaign(
        **data.model_dump(by_alias=False, exclude={"metadata"}), metadata_=data.metadata
    )
    db.add(campaign)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise ConflictError("A campaign with this slug already exists") from exc
    await db.refresh(campaign)
    return campaign


async def update_campaign(db: AsyncSession, campaign_id: UUID, data: CampaignUpdate) -> Campaign:
    campaign = await get_campaign(db, campaign_id)
    values = data.model_dump(exclude_unset=True, exclude={"metadata"})
    for field, value in values.items():
        setattr(campaign, field, value)
    if "metadata" in data.model_fields_set:
        campaign.metadata_ = data.metadata or {}
    await db.commit()
    await db.refresh(campaign)
    return campaign


async def archive_campaign(db: AsyncSession, campaign_id: UUID) -> None:
    campaign = await get_campaign(db, campaign_id)
    campaign.archived_at = datetime.now(UTC)
    await db.commit()


async def list_sessions(db: AsyncSession, campaign_id: UUID) -> list[CampaignSession]:
    await get_campaign(db, campaign_id)
    rows = await db.scalars(
        select(CampaignSession)
        .where(CampaignSession.campaign_id == campaign_id)
        .order_by(CampaignSession.session_number)
    )
    return list(rows)


async def create_session(
    db: AsyncSession, campaign_id: UUID, data: SessionCreate
) -> CampaignSession:
    await get_campaign(db, campaign_id)
    item = CampaignSession(campaign_id=campaign_id, **data.model_dump())
    db.add(item)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise ConflictError("Session number already exists in this campaign") from exc
    await db.refresh(item)
    return item


async def update_session(
    db: AsyncSession, campaign_id: UUID, session_id: UUID, data: SessionUpdate
) -> CampaignSession:
    item = await db.scalar(
        select(CampaignSession).where(
            CampaignSession.id == session_id, CampaignSession.campaign_id == campaign_id
        )
    )
    if item is None:
        raise NotFoundError("Session not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    if (
        item.in_game_start_year
        and item.in_game_end_year
        and item.in_game_end_year < item.in_game_start_year
    ):
        raise ConflictError("in_game_end_year must not precede in_game_start_year")
    await db.commit()
    await db.refresh(item)
    return item
