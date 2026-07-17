from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import Field, field_validator, model_validator

from app.schemas.common import ORMModel


class CampaignCreate(ORMModel):
    name: str = Field(min_length=1, max_length=200)
    slug: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=100)
    description: str | None = None
    current_year: int = Field(default=485, ge=1, le=9999)
    ruleset_version: str = "Pendragon 6th Edition"
    timezone: str = "UTC"
    metadata: dict[str, Any] = Field(
        default_factory=dict, validation_alias="metadata_", serialization_alias="metadata"
    )

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("name cannot be blank")
        return value.strip()


class CampaignUpdate(ORMModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    current_year: int | None = Field(default=None, ge=1, le=9999)
    timezone: str | None = None
    metadata: dict[str, Any] | None = None


class CampaignRead(CampaignCreate):
    id: UUID
    archived_at: datetime | None
    created_at: datetime
    updated_at: datetime


class SessionCreate(ORMModel):
    session_number: int = Field(gt=0)
    title: str = Field(min_length=1, max_length=300)
    summary: str | None = None
    played_at: datetime | None = None
    in_game_start_year: int | None = Field(default=None, ge=1, le=9999)
    in_game_end_year: int | None = Field(default=None, ge=1, le=9999)
    status: Literal["planned", "in_progress", "completed", "cancelled"] = "planned"

    @model_validator(mode="after")
    def valid_year_range(self) -> "SessionCreate":
        if (
            self.in_game_start_year
            and self.in_game_end_year
            and self.in_game_end_year < self.in_game_start_year
        ):
            raise ValueError("in_game_end_year must not precede in_game_start_year")
        return self


class SessionUpdate(ORMModel):
    title: str | None = Field(default=None, min_length=1, max_length=300)
    summary: str | None = None
    played_at: datetime | None = None
    in_game_start_year: int | None = Field(default=None, ge=1, le=9999)
    in_game_end_year: int | None = Field(default=None, ge=1, le=9999)
    status: Literal["planned", "in_progress", "completed", "cancelled"] | None = None


class SessionRead(SessionCreate):
    id: UUID
    campaign_id: UUID
    created_at: datetime
    updated_at: datetime
