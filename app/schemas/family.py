from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import Field, model_validator

from app.schemas.character import KnowledgeScopeValue
from app.schemas.common import ORMModel


class FamilyCreate(ORMModel):
    name: str = Field(min_length=1, max_length=300)
    founding_year: int | None = Field(default=None, ge=1, le=9999)
    dissolved_year: int | None = Field(default=None, ge=1, le=9999)
    origin_location_id: UUID | None = None
    culture: str | None = None
    religion: str | None = None
    coat_of_arms: str | None = None
    motto: str | None = None
    scope: KnowledgeScopeValue = "players"
    notes: str | None = None
    metadata: dict[str, Any] = Field(
        default_factory=dict, validation_alias="metadata_", serialization_alias="metadata"
    )

    @model_validator(mode="after")
    def valid_years(self):
        if self.founding_year and self.dissolved_year and self.dissolved_year < self.founding_year:
            raise ValueError("dissolved_year cannot precede founding_year")
        return self


class FamilyRead(FamilyCreate):
    id: UUID
    campaign_id: UUID
    archived_at: datetime | None
    created_at: datetime
    updated_at: datetime


class FamilyMembershipCreate(ORMModel):
    character_id: UUID
    membership_type: str = Field(default="birth", min_length=1)
    branch_name: str | None = None
    start_year: int | None = Field(default=None, ge=1, le=9999)
    end_year: int | None = Field(default=None, ge=1, le=9999)
    start_event_id: UUID | None = None
    end_event_id: UUID | None = None
    is_primary: bool = True
    scope: KnowledgeScopeValue = "players"


class FamilyMembershipRead(FamilyMembershipCreate):
    id: UUID
    campaign_id: UUID
    family_id: UUID
    created_at: datetime


class ParentageCreate(ORMModel):
    parent_character_id: UUID
    child_character_id: UUID
    relationship_type: str = Field(default="biological", min_length=1)
    certainty: str = Field(default="confirmed", min_length=1)
    event_id: UUID | None = None
    scope: KnowledgeScopeValue = "players"
    notes: str | None = None

    @model_validator(mode="after")
    def distinct_people(self):
        if self.parent_character_id == self.child_character_id:
            raise ValueError("parent and child must be different characters")
        return self


class ParentageRead(ParentageCreate):
    id: UUID
    campaign_id: UUID
    created_at: datetime


class MarriageCreate(ORMModel):
    spouse_one_id: UUID
    spouse_two_id: UUID
    start_event_id: UUID | None = None
    end_event_id: UUID | None = None
    start_year: int = Field(ge=1, le=9999)
    end_year: int | None = Field(default=None, ge=1, le=9999)
    end_reason: str | None = None
    scope: KnowledgeScopeValue = "players"
    notes: str | None = None

    @model_validator(mode="after")
    def valid_marriage(self):
        if self.spouse_one_id == self.spouse_two_id:
            raise ValueError("spouses must be different characters")
        if self.end_year and self.end_year < self.start_year:
            raise ValueError("end_year cannot precede start_year")
        return self


class MarriageRead(MarriageCreate):
    id: UUID
    campaign_id: UUID
    created_at: datetime


class InheritanceCaseCreate(ORMModel):
    decedent_character_id: UUID
    opened_event_id: UUID | None = None
    settled_event_id: UUID | None = None
    opened_year: int = Field(ge=1, le=9999)
    settled_year: int | None = Field(default=None, ge=1, le=9999)
    governing_custom: str | None = None
    will_summary: str | None = None
    scope: KnowledgeScopeValue = "players"
    notes: str | None = None


class InheritanceCaseRead(InheritanceCaseCreate):
    id: UUID
    campaign_id: UUID
    created_at: datetime


class InheritanceHeirCreate(ORMModel):
    character_id: UUID
    priority: int | None = Field(default=None, gt=0)
    relationship_description: str | None = None
    claim_status: str = Field(default="potential", min_length=1)
    designated: bool = False
    notes: str | None = None


class InheritanceHeirRead(InheritanceHeirCreate):
    id: UUID
    campaign_id: UUID
    inheritance_case_id: UUID
    created_at: datetime


class InheritanceTransferCreate(ORMModel):
    manor_id: UUID
    beneficiary_character_id: UUID
    event_id: UUID
    transferred_year: int = Field(ge=1, le=9999)
    terms: str | None = None


class InheritanceTransferRead(InheritanceTransferCreate):
    id: UUID
    campaign_id: UUID
    inheritance_case_id: UUID
    created_at: datetime


class SourceReferenceCreate(ORMModel):
    source_type: str = Field(default="book", min_length=1)
    title: str = Field(min_length=1)
    edition: str | None = None
    publication_year: int | None = Field(default=None, gt=0)
    notes: str | None = None


class SourceReferenceRead(SourceReferenceCreate):
    id: UUID
    campaign_id: UUID
    created_at: datetime


class FamilyHistoryCreate(ORMModel):
    ancestor_character_id: UUID | None = None
    realm_location_id: UUID | None = None
    source_reference_id: UUID | None = None
    dice_log_id: UUID | None = None
    start_year: int = Field(ge=1, le=9999)
    end_year: int | None = Field(default=None, ge=1, le=9999)
    entry_type: str = Field(default="annual_service", min_length=1)
    title: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    generation_method: str = Field(default="manual", min_length=1)
    source_locator: str | None = None
    roll_expression: str | None = None
    roll_result: str | None = None
    scope: KnowledgeScopeValue = "players"
    metadata: dict[str, Any] = Field(
        default_factory=dict, validation_alias="metadata_", serialization_alias="metadata"
    )
    glory_amount: int | None = None
    glory_category: str = "ancestral"
    glory_reason: str | None = None

    @model_validator(mode="after")
    def valid_years(self):
        if self.end_year and self.end_year < self.start_year:
            raise ValueError("end_year cannot precede start_year")
        if self.glory_amount is not None and self.ancestor_character_id is None:
            raise ValueError("ancestor_character_id is required when recording Glory")
        return self


class FamilyHistoryRead(ORMModel):
    id: UUID
    campaign_id: UUID
    family_id: UUID
    ancestor_character_id: UUID | None
    event_id: UUID
    realm_location_id: UUID | None
    source_reference_id: UUID | None
    dice_log_id: UUID | None
    glory_ledger_id: UUID | None
    start_year: int
    end_year: int | None
    entry_type: str
    title: str
    summary: str
    generation_method: str
    source_locator: str | None
    roll_expression: str | None
    roll_result: str | None
    scope: KnowledgeScopeValue
    metadata: dict[str, Any] = Field(validation_alias="metadata_", serialization_alias="metadata")
    created_at: datetime
