from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.schemas.common import ORMModel


class WinterPhaseCreate(ORMModel):
    in_game_year: int = Field(ge=1, le=9999)
    status: str = Field(default="recorded", min_length=1, max_length=100)
    notes: str | None = None


class WinterPhaseRead(WinterPhaseCreate):
    id: UUID
    campaign_id: UUID
    event_id: UUID
    created_at: datetime


class WinterParticipantRead(ORMModel):
    id: UUID
    campaign_id: UUID
    winter_phase_id: UUID
    character_id: UUID
    history_entry_id: UUID | None
    created_at: datetime


class CharacterHistoryRead(ORMModel):
    id: UUID
    campaign_id: UUID
    character_id: UUID
    event_id: UUID
    source_key: str
    in_game_year: int
    title: str
    source: str | None
    description: str | None
    reported_glory: int
    favour_value: int
    created_at: datetime


class CharacterWoundRead(ORMModel):
    id: UUID
    campaign_id: UUID
    character_id: UUID
    event_id: UUID | None
    source_key: str
    effective_year: int
    sequence: int
    damage: int
    treated: bool
    wound_source: str | None
    description: str | None
    reason: str | None
    recorded_at: datetime
