from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import Field, model_validator

from app.schemas.common import ORMModel

KnowledgeScopeValue = Literal["gm_only", "players", "shared"]


class CharacterCreate(ORMModel):
    kind: Literal["player_knight", "npc"]
    name: str = Field(min_length=1, max_length=300)
    epithet: str | None = None
    player_name: str | None = None
    gender: str | None = None
    culture: str | None = None
    religion: str | None = None
    social_class: str | None = None
    birth_year: int | None = Field(default=None, ge=1, le=9999)
    status: Literal["alive", "dead", "missing", "unknown"] = "alive"
    coat_of_arms: str | None = None
    public_description: str | None = None
    foundry_uuid: str | None = Field(default=None, max_length=500)
    metadata: dict[str, Any] = Field(
        default_factory=dict, validation_alias="metadata_", serialization_alias="metadata"
    )

    @model_validator(mode="after")
    def player_knight_has_player(self) -> "CharacterCreate":
        if self.kind == "player_knight" and not (self.player_name and self.player_name.strip()):
            raise ValueError("player_name is required for a player knight")
        return self


class CharacterUpdate(ORMModel):
    name: str | None = Field(default=None, min_length=1, max_length=300)
    epithet: str | None = None
    player_name: str | None = None
    gender: str | None = None
    culture: str | None = None
    religion: str | None = None
    social_class: str | None = None
    birth_year: int | None = Field(default=None, ge=1, le=9999)
    coat_of_arms: str | None = None
    public_description: str | None = None
    foundry_uuid: str | None = Field(default=None, max_length=500)
    metadata: dict[str, Any] | None = None


class CharacterRead(CharacterCreate):
    id: UUID
    campaign_id: UUID
    archived_at: datetime | None
    created_at: datetime
    updated_at: datetime


class CharacterNoteCreate(ORMModel):
    event_id: UUID | None = None
    session_id: UUID | None = None
    scope: KnowledgeScopeValue = "gm_only"
    note_type: str = Field(default="general", min_length=1, max_length=100)
    title: str | None = Field(default=None, max_length=300)
    body: str = Field(min_length=1)


class CharacterNoteRead(CharacterNoteCreate):
    id: UUID
    campaign_id: UUID
    character_id: UUID
    recorded_at: datetime


class CharacterStatusCreate(ORMModel):
    event_id: UUID | None = None
    session_id: UUID | None = None
    status: Literal["alive", "dead", "missing", "unknown"]
    effective_year: int = Field(ge=1, le=9999)
    sequence: int = Field(default=0, ge=0)
    reason: str | None = None


class CharacterStatusRead(CharacterStatusCreate):
    id: UUID
    campaign_id: UUID
    character_id: UUID
    recorded_at: datetime


class TraitDefinitionCreate(ORMModel):
    name: str = Field(min_length=1, max_length=100)
    opposed_name: str = Field(min_length=1, max_length=100)
    description: str | None = None


class TraitDefinitionRead(TraitDefinitionCreate):
    id: UUID
    campaign_id: UUID
    created_at: datetime


class TraitLedgerCreate(ORMModel):
    trait_definition_id: UUID
    event_id: UUID | None = None
    session_id: UUID | None = None
    effective_year: int = Field(ge=1, le=9999)
    sequence: int = Field(default=0, ge=0)
    trait_value: int = Field(ge=0)
    opposed_value: int = Field(ge=0)
    reason: str | None = None


class TraitLedgerRead(TraitLedgerCreate):
    id: UUID
    campaign_id: UUID
    character_id: UUID
    recorded_at: datetime


class SkillDefinitionCreate(ORMModel):
    name: str = Field(min_length=1, max_length=100)
    category: str = Field(default="ordinary", min_length=1, max_length=100)
    description: str | None = None


class SkillDefinitionRead(SkillDefinitionCreate):
    id: UUID
    campaign_id: UUID
    created_at: datetime


class SkillLedgerCreate(ORMModel):
    skill_definition_id: UUID
    event_id: UUID | None = None
    session_id: UUID | None = None
    effective_year: int = Field(ge=1, le=9999)
    sequence: int = Field(default=0, ge=0)
    value: int = Field(ge=0)
    reason: str | None = None


class SkillLedgerRead(SkillLedgerCreate):
    id: UUID
    campaign_id: UUID
    character_id: UUID
    recorded_at: datetime


class PassionCreate(ORMModel):
    name: str = Field(min_length=1, max_length=150)
    subject_text: str | None = None
    related_character_id: UUID | None = None
    scope: KnowledgeScopeValue = "players"
    started_event_id: UUID | None = None
    started_year: int | None = Field(default=None, ge=1, le=9999)


class PassionRead(PassionCreate):
    id: UUID
    campaign_id: UUID
    character_id: UUID
    ended_event_id: UUID | None
    ended_year: int | None
    created_at: datetime


class PassionLedgerCreate(ORMModel):
    event_id: UUID | None = None
    session_id: UUID | None = None
    effective_year: int = Field(ge=1, le=9999)
    sequence: int = Field(default=0, ge=0)
    value: int = Field(ge=0)
    reason: str | None = None


class PassionLedgerRead(PassionLedgerCreate):
    id: UUID
    campaign_id: UUID
    passion_id: UUID
    recorded_at: datetime


class GloryCreate(ORMModel):
    event_id: UUID | None = None
    session_id: UUID | None = None
    awarded_year: int = Field(ge=1, le=9999)
    sequence: int = Field(default=0, ge=0)
    amount: int
    category: str = Field(default="other", min_length=1, max_length=100)
    reason: str = Field(min_length=1)
    scope: KnowledgeScopeValue = "players"

    @model_validator(mode="after")
    def nonzero_amount(self) -> "GloryCreate":
        if self.amount == 0:
            raise ValueError("amount must not be zero")
        return self


class GloryRead(GloryCreate):
    id: UUID
    campaign_id: UUID
    character_id: UUID
    recorded_at: datetime


class GlorySummary(ORMModel):
    character_id: UUID
    total: int
    entries: list[GloryRead]
