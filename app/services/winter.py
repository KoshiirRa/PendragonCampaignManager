from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    CharacterHistoryEntry,
    CharacterWoundLedger,
    Event,
    EventVisibility,
    WinterPhase,
    WinterPhaseParticipant,
)
from app.schemas.winter import WinterPhaseCreate
from app.services.campaigns import get_campaign
from app.services.errors import ConflictError, NotFoundError


async def list_phases(db: AsyncSession, campaign_id: UUID) -> list[WinterPhase]:
    await get_campaign(db, campaign_id)
    return list(
        await db.scalars(
            select(WinterPhase)
            .where(WinterPhase.campaign_id == campaign_id)
            .order_by(WinterPhase.in_game_year)
        )
    )


async def create_phase(db: AsyncSession, campaign_id: UUID, data: WinterPhaseCreate) -> WinterPhase:
    await get_campaign(db, campaign_id)
    existing = await db.scalar(
        select(WinterPhase).where(
            WinterPhase.campaign_id == campaign_id,
            WinterPhase.in_game_year == data.in_game_year,
        )
    )
    if existing:
        raise ConflictError("Winter Phase already exists for this campaign year")
    event = Event(
        campaign_id=campaign_id,
        event_type="winter_phase",
        title=f"Winter Phase {data.in_game_year}",
        description=data.notes,
        in_game_year=data.in_game_year,
        visibility=EventVisibility.PLAYERS,
    )
    db.add(event)
    await db.flush()
    phase = WinterPhase(campaign_id=campaign_id, event_id=event.id, **data.model_dump())
    db.add(phase)
    await db.commit()
    await db.refresh(phase)
    return phase


async def list_participants(
    db: AsyncSession, campaign_id: UUID, phase_id: UUID
) -> list[WinterPhaseParticipant]:
    phase = await db.get(WinterPhase, phase_id)
    if phase is None or phase.campaign_id != campaign_id:
        raise NotFoundError("Winter Phase not found")
    return list(
        await db.scalars(
            select(WinterPhaseParticipant)
            .where(WinterPhaseParticipant.winter_phase_id == phase_id)
            .order_by(WinterPhaseParticipant.created_at)
        )
    )


async def list_character_history(
    db: AsyncSession, campaign_id: UUID, character_id: UUID
) -> list[CharacterHistoryEntry]:
    return list(
        await db.scalars(
            select(CharacterHistoryEntry)
            .where(
                CharacterHistoryEntry.campaign_id == campaign_id,
                CharacterHistoryEntry.character_id == character_id,
            )
            .order_by(CharacterHistoryEntry.in_game_year, CharacterHistoryEntry.created_at)
        )
    )


async def list_character_wounds(
    db: AsyncSession, campaign_id: UUID, character_id: UUID
) -> list[CharacterWoundLedger]:
    return list(
        await db.scalars(
            select(CharacterWoundLedger)
            .where(
                CharacterWoundLedger.campaign_id == campaign_id,
                CharacterWoundLedger.character_id == character_id,
            )
            .order_by(
                CharacterWoundLedger.effective_year,
                CharacterWoundLedger.sequence,
                CharacterWoundLedger.recorded_at,
            )
        )
    )
