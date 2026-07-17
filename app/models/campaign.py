from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Campaign(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "campaigns"
    __table_args__ = (
        CheckConstraint("btrim(name) <> ''", name="name_not_blank"),
        CheckConstraint("slug ~ '^[a-z0-9]+(?:-[a-z0-9]+)*$'", name="slug_format"),
    )

    name: Mapped[str] = mapped_column(String, nullable=False)
    slug: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    current_year: Mapped[int] = mapped_column(SmallInteger, default=485)
    ruleset_version: Mapped[str] = mapped_column(String, default="Pendragon 6th Edition")
    timezone: Mapped[str] = mapped_column(String, default="UTC")
    metadata_: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, default=dict)
    archived_at: Mapped[datetime | None]

    sessions: Mapped[list[CampaignSession]] = relationship(back_populates="campaign")


class CampaignSession(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "campaign_sessions"
    __table_args__ = (
        UniqueConstraint("campaign_id", "session_number"),
        CheckConstraint("session_number > 0", name="positive_number"),
        CheckConstraint("btrim(title) <> ''", name="title_not_blank"),
    )

    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    session_number: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String)
    summary: Mapped[str | None] = mapped_column(Text)
    played_at: Mapped[datetime | None]
    in_game_start_year: Mapped[int | None] = mapped_column(SmallInteger)
    in_game_end_year: Mapped[int | None] = mapped_column(SmallInteger)
    status: Mapped[str] = mapped_column(String, default="planned")

    campaign: Mapped[Campaign] = relationship(back_populates="sessions")
