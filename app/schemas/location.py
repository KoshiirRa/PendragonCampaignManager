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
