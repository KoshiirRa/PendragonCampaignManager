from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, SmallInteger, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKeyMixin


class Event(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "events"

    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    session_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("campaign_sessions.id", ondelete="SET NULL")
    )
    event_type: Mapped[str] = mapped_column(String)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(Text)
    in_game_year: Mapped[int] = mapped_column(SmallInteger)
    in_game_date: Mapped[str | None] = mapped_column(String)
    sequence: Mapped[int] = mapped_column(Integer, default=0)
    visibility: Mapped[str] = mapped_column(String, default="players")
    occurred_at: Mapped[datetime | None]
    recorded_at: Mapped[datetime] = mapped_column(server_default=func.now())
    supersedes_event_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("events.id", ondelete="RESTRICT")
    )
    metadata_: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, default=dict)


class EventLink(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "event_links"

    event_id: Mapped[UUID] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"))
    entity_type: Mapped[str] = mapped_column(String)
    entity_id: Mapped[UUID]
    role: Mapped[str] = mapped_column(String, default="subject")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class DiceLog(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "dice_logs"

    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    session_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("campaign_sessions.id", ondelete="SET NULL")
    )
    event_id: Mapped[UUID | None] = mapped_column(ForeignKey("events.id", ondelete="SET NULL"))
    roller_type: Mapped[str] = mapped_column(String)
    roller_id: Mapped[UUID | None]
    expression: Mapped[str] = mapped_column(String)
    individual_rolls: Mapped[list[int]] = mapped_column(ARRAY(SmallInteger))
    modifier: Mapped[int] = mapped_column(SmallInteger, default=0)
    total: Mapped[int] = mapped_column(Integer)
    target_number: Mapped[int | None] = mapped_column(SmallInteger)
    outcome: Mapped[str | None] = mapped_column(String)
    purpose: Mapped[str | None] = mapped_column(Text)
    rolled_at: Mapped[datetime] = mapped_column(server_default=func.now())
    metadata_: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, default=dict)
