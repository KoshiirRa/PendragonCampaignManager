from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import Field

from app.schemas.common import ORMModel


class EventCreate(ORMModel):
    session_id: UUID | None = None
    event_type: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=300)
    description: str | None = None
    in_game_year: int = Field(ge=1, le=9999)
    in_game_date: str | None = None
    sequence: int = Field(default=0, ge=0)
    visibility: Literal["gm_only", "players", "public"] = "players"
    occurred_at: datetime | None = None
    supersedes_event_id: UUID | None = None
    metadata: dict[str, Any] = Field(
        default_factory=dict, validation_alias="metadata_", serialization_alias="metadata"
    )


class EventRead(EventCreate):
    id: UUID
    campaign_id: UUID
    recorded_at: datetime


class DiceLogCreate(ORMModel):
    session_id: UUID | None = None
    event_id: UUID | None = None
    roller_type: str = Field(min_length=1, max_length=50)
    roller_id: UUID | None = None
    expression: str = Field(min_length=1, max_length=50)
    individual_rolls: list[int] = Field(min_length=1)
    modifier: int = 0
    total: int
    target_number: int | None = None
    outcome: str | None = None
    purpose: str | None = None
    metadata: dict[str, Any] = Field(
        default_factory=dict, validation_alias="metadata_", serialization_alias="metadata"
    )


class DiceLogRead(DiceLogCreate):
    id: UUID
    campaign_id: UUID
    rolled_at: datetime
