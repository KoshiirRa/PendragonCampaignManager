from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    AnnualChronicle,
    AnnualChronicleSection,
    AnnualChronicleSource,
    Character,
    CharacterHistoryEntry,
    CharacterKind,
    CharacterWoundLedger,
    Event,
    EventLink,
    EventVisibility,
    WinterPhase,
    WinterPhaseParticipant,
)
from app.schemas.winter import AnnualChronicleRead, AnnualChronicleSectionRead, WinterPhaseCreate
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
    await db.flush()
    await _generate_chronicle(db, campaign_id, phase)
    await db.commit()
    await db.refresh(phase)
    return phase


def _event_sentence(event: Event) -> str:
    detail = (event.description or "").strip()
    if detail:
        detail = detail[0].lower() + detail[1:] if not detail[0].isupper() else detail
        return f"In {event.in_game_date or 'the course of the year'}, {detail.rstrip('.')}."
    return f"The rolls remember {event.title.rstrip('.').lower()}."


async def _generate_chronicle(
    db: AsyncSession, campaign_id: UUID, phase: WinterPhase
) -> AnnualChronicle:
    superseded_ids = select(Event.supersedes_event_id).where(
        Event.campaign_id == campaign_id,
        Event.supersedes_event_id.is_not(None),
    )
    events = list(
        await db.scalars(
            select(Event)
            .where(
                Event.campaign_id == campaign_id,
                Event.in_game_year == phase.in_game_year,
                Event.visibility.in_((EventVisibility.PLAYERS, EventVisibility.PUBLIC)),
                Event.id.not_in(superseded_ids),
                Event.id != phase.event_id,
            )
            .order_by(Event.sequence, Event.recorded_at)
        )
    )
    knights = list(
        await db.scalars(
            select(Character)
            .where(
                Character.campaign_id == campaign_id,
                Character.kind == CharacterKind.PLAYER_KNIGHT,
                Character.archived_at.is_(None),
            )
            .order_by(Character.name)
        )
    )
    revision = (
        await db.scalar(
            select(func.max(AnnualChronicle.revision)).where(
                AnnualChronicle.campaign_id == campaign_id,
                AnnualChronicle.in_game_year == phase.in_game_year,
            )
        )
        or 0
    ) + 1
    chronicle = AnnualChronicle(
        campaign_id=campaign_id,
        winter_phase_id=phase.id,
        in_game_year=phase.in_game_year,
        revision=revision,
        title=f"The Chronicle of the Year {phase.in_game_year}",
        opening=(
            f"Here is set down the memory of the year {phase.in_game_year}, "
            "that worthy deeds, hard choices, and the turns of fortune should not be lost."
        ),
        closing=(
            "Thus the year was brought to its winter reckoning, and each knight returned "
            "to hall and hearth bearing the honor and burden of what had passed."
        ),
        status="published",
        generator_version="chronicle-template-v1",
    )
    db.add(chronicle)
    await db.flush()

    links = (
        await db.execute(
            select(EventLink.event_id, EventLink.entity_id).where(
                EventLink.event_id.in_([event.id for event in events] or [phase.event_id]),
                EventLink.entity_type == "character",
            )
        )
    ).all()
    event_character_ids: dict[UUID, set[UUID]] = {}
    for event_id, character_id in links:
        event_character_ids.setdefault(event_id, set()).add(character_id)

    for position, knight in enumerate(knights):
        knight_events = [
            event for event in events if knight.id in event_character_ids.get(event.id, set())
        ]
        body = " ".join(_event_sentence(event) for event in knight_events)
        if not body:
            body = (
                f"Of {knight.name}, the rolls preserve no particular deed for this year; "
                "yet the knight endured the season and came again to the winter accounting."
            )
        section = AnnualChronicleSection(
            campaign_id=campaign_id,
            chronicle_id=chronicle.id,
            character_id=knight.id,
            position=position,
            heading=f"Of {knight.name}",
            body=body,
        )
        db.add(section)
        await db.flush()
        for event in knight_events:
            db.add(
                AnnualChronicleSource(
                    campaign_id=campaign_id,
                    chronicle_id=chronicle.id,
                    section_id=section.id,
                    event_id=event.id,
                )
            )
    return chronicle


async def _chronicle_read(db: AsyncSession, chronicle: AnnualChronicle) -> AnnualChronicleRead:
    sections = list(
        await db.scalars(
            select(AnnualChronicleSection)
            .where(AnnualChronicleSection.chronicle_id == chronicle.id)
            .order_by(AnnualChronicleSection.position)
        )
    )
    sources = (
        await db.execute(
            select(AnnualChronicleSource.section_id, AnnualChronicleSource.event_id).where(
                AnnualChronicleSource.chronicle_id == chronicle.id
            )
        )
    ).all()
    by_section: dict[UUID | None, list[UUID]] = {}
    for section_id, event_id in sources:
        by_section.setdefault(section_id, []).append(event_id)
    return AnnualChronicleRead(
        id=chronicle.id,
        campaign_id=chronicle.campaign_id,
        winter_phase_id=chronicle.winter_phase_id,
        in_game_year=chronicle.in_game_year,
        revision=chronicle.revision,
        title=chronicle.title,
        opening=chronicle.opening,
        closing=chronicle.closing,
        status=chronicle.status,
        generator_version=chronicle.generator_version,
        created_at=chronicle.created_at,
        source_event_ids=list(dict.fromkeys(event_id for _, event_id in sources)),
        sections=[
            AnnualChronicleSectionRead(
                id=section.id,
                character_id=section.character_id,
                position=section.position,
                heading=section.heading,
                body=section.body,
                source_event_ids=by_section.get(section.id, []),
            )
            for section in sections
        ],
    )


async def get_chronicle(db: AsyncSession, campaign_id: UUID, year: int) -> AnnualChronicleRead:
    await get_campaign(db, campaign_id)
    chronicle = await db.scalar(
        select(AnnualChronicle)
        .where(
            AnnualChronicle.campaign_id == campaign_id,
            AnnualChronicle.in_game_year == year,
        )
        .order_by(AnnualChronicle.revision.desc())
        .limit(1)
    )
    if chronicle is None:
        raise NotFoundError("Annual chronicle not found")
    return await _chronicle_read(db, chronicle)


async def generate_chronicle(db: AsyncSession, campaign_id: UUID, year: int) -> AnnualChronicleRead:
    await get_campaign(db, campaign_id)
    phase = await db.scalar(
        select(WinterPhase).where(
            WinterPhase.campaign_id == campaign_id,
            WinterPhase.in_game_year == year,
        )
    )
    if phase is None:
        raise ConflictError("A Winter Phase must exist before its chronicle can be generated")
    chronicle = await _generate_chronicle(db, campaign_id, phase)
    await db.commit()
    await db.refresh(chronicle)
    return await _chronicle_read(db, chronicle)


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
