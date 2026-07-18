from datetime import datetime
from decimal import Decimal
from typing import Any, Literal
from uuid import UUID

from pydantic import Field, model_validator

from app.schemas.character import KnowledgeScopeValue
from app.schemas.common import ORMModel

LocationKindValue = Literal[
    "kingdom",
    "county",
    "barony",
    "manor",
    "holding",
    "settlement",
    "castle",
    "church",
    "forest",
    "road",
    "other",
]


class LocationCreate(ORMModel):
    parent_location_id: UUID | None = None
    kind: LocationKindValue
    name: str = Field(min_length=1, max_length=300)
    description: str | None = None
    scope: KnowledgeScopeValue = "players"
    latitude: Decimal | None = Field(default=None, ge=-90, le=90)
    longitude: Decimal | None = Field(default=None, ge=-180, le=180)
    metadata: dict[str, Any] = Field(
        default_factory=dict, validation_alias="metadata_", serialization_alias="metadata"
    )


class LocationUpdate(ORMModel):
    parent_location_id: UUID | None = None
    name: str | None = Field(default=None, min_length=1, max_length=300)
    description: str | None = None
    scope: KnowledgeScopeValue | None = None
    latitude: Decimal | None = Field(default=None, ge=-90, le=90)
    longitude: Decimal | None = Field(default=None, ge=-180, le=180)
    metadata: dict[str, Any] | None = None


class LocationRead(LocationCreate):
    id: UUID
    campaign_id: UUID
    archived_at: datetime | None
    created_at: datetime
    updated_at: datetime


class ManorCreate(ORMModel):
    location: LocationCreate
    customary_income: Decimal | None = Field(default=None, ge=0)
    assized_rent: Decimal | None = Field(default=None, ge=0)
    population: int | None = Field(default=None, ge=0)
    base_defensive_value: int = Field(default=1, ge=0)
    acreage: int | None = Field(default=None, ge=0)
    notes: str | None = None

    @model_validator(mode="after")
    def location_is_manor(self) -> "ManorCreate":
        if self.location.kind != "manor":
            raise ValueError("location kind must be manor")
        return self


class ManorRead(ORMModel):
    id: UUID
    campaign_id: UUID
    location_id: UUID
    customary_income: Decimal | None
    assized_rent: Decimal | None
    population: int | None
    base_defensive_value: int
    acreage: int | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


class ManorTenureCreate(ORMModel):
    holder_character_id: UUID
    liege_character_id: UUID | None = None
    start_event_id: UUID | None = None
    start_year: int = Field(ge=1, le=9999)
    tenure_type: str = Field(default="grant", min_length=1, max_length=100)
    terms: str | None = None


class ManorTenureRead(ManorTenureCreate):
    id: UUID
    campaign_id: UUID
    manor_id: UUID
    end_event_id: UUID | None
    end_year: int | None
    created_at: datetime


class ManorImprovementCreate(ORMModel):
    name: str = Field(min_length=1, max_length=200)
    improvement_type: str = Field(min_length=1, max_length=100)
    description: str | None = None


class ManorImprovementRead(ManorImprovementCreate):
    id: UUID
    campaign_id: UUID
    manor_id: UUID
    created_at: datetime


class ManorImprovementLedgerCreate(ORMModel):
    event_id: UUID | None = None
    effective_year: int = Field(ge=1, le=9999)
    status: str = Field(min_length=1, max_length=100)
    income_modifier: Decimal = Decimal("0")
    maintenance_cost: Decimal = Field(default=Decimal("0"), ge=0)
    notes: str | None = None


class ManorImprovementLedgerRead(ManorImprovementLedgerCreate):
    id: UUID
    campaign_id: UUID
    improvement_id: UUID
    recorded_at: datetime


class ManorAnnualResolutionCreate(ORMModel):
    winter_phase_id: UUID | None = None
    in_game_year: int = Field(ge=1, le=9999)
    steward_character_id: UUID | None = None
    stewardship_value: int | None = Field(default=None, ge=0)
    roll_result: str = Field(min_length=1, max_length=100)
    income: Decimal = Decimal("0")
    expenses: Decimal = Field(default=Decimal("0"), ge=0)
    privy_funds: Decimal = Decimal("0")
    famine_stage: int = Field(default=0, ge=0)
    population_change: int = 0
    notes: str | None = None


class ManorAnnualResolutionRead(ManorAnnualResolutionCreate):
    id: UUID
    campaign_id: UUID
    manor_id: UUID
    event_id: UUID
    created_at: datetime


class TreasuryEntryCreate(ORMModel):
    event_id: UUID | None = None
    annual_resolution_id: UUID | None = None
    in_game_year: int = Field(ge=1, le=9999)
    amount: Decimal
    category: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1)

    @model_validator(mode="after")
    def amount_is_nonzero(self):
        if self.amount == 0:
            raise ValueError("amount must not be zero")
        return self


class TreasuryEntryRead(TreasuryEntryCreate):
    id: UUID
    campaign_id: UUID
    manor_id: UUID
    created_at: datetime


class ManorAssetCreate(ORMModel):
    asset_type: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None


class ManorAssetRead(ManorAssetCreate):
    id: UUID
    campaign_id: UUID
    manor_id: UUID
    created_at: datetime


class ManorAssetEntryCreate(ORMModel):
    event_id: UUID | None = None
    effective_year: int = Field(ge=1, le=9999)
    quantity: Decimal | None = Field(default=None, ge=0)
    status: str = Field(min_length=1, max_length=100)
    annual_income: Decimal = Decimal("0")
    annual_cost: Decimal = Field(default=Decimal("0"), ge=0)
    notes: str | None = None


class ManorAssetEntryRead(ManorAssetEntryCreate):
    id: UUID
    campaign_id: UUID
    asset_id: UUID
    recorded_at: datetime


class HouseholdEmploymentCreate(ORMModel):
    character_id: UUID | None = None
    name: str = Field(min_length=1, max_length=200)
    role: str = Field(min_length=1, max_length=100)
    social_rank: str | None = None
    key_skill: str | None = None
    key_skill_value: int | None = Field(default=None, ge=0)
    annual_cost: Decimal = Field(default=Decimal("0"), ge=0)
    start_year: int = Field(ge=1, le=9999)
    end_year: int | None = Field(default=None, ge=1, le=9999)
    notes: str | None = None


class HouseholdEmploymentRead(HouseholdEmploymentCreate):
    id: UUID
    campaign_id: UUID
    manor_id: UUID
    start_event_id: UUID | None
    end_event_id: UUID | None
    created_at: datetime


class DefenseLayerCreate(ORMModel):
    name: str = Field(min_length=1, max_length=200)
    ring_order: int = Field(ge=0)
    defensive_value: int
    construction_cost: Decimal | None = Field(default=None, ge=0)
    improvement_id: UUID | None = None


class DefenseLayerRead(DefenseLayerCreate):
    id: UUID
    campaign_id: UUID
    manor_id: UUID
