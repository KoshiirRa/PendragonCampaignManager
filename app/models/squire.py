from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, SmallInteger, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKeyMixin


class Squire(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "squires"
    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    character_id: Mapped[UUID] = mapped_column(
        ForeignKey("characters.id", ondelete="RESTRICT"), unique=True
    )
    source_key: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class SquireServiceHistory(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "squire_service_history"
    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    squire_id: Mapped[UUID] = mapped_column(ForeignKey("squires.id", ondelete="RESTRICT"))
    knight_character_id: Mapped[UUID] = mapped_column(
        ForeignKey("characters.id", ondelete="RESTRICT")
    )
    source_key: Mapped[str] = mapped_column(Text)
    start_year: Mapped[int] = mapped_column(SmallInteger)
    end_year: Mapped[int | None] = mapped_column(SmallInteger)
    start_event_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("events.id", ondelete="SET NULL")
    )
    end_event_id: Mapped[UUID | None] = mapped_column(ForeignKey("events.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class SquireStateLedger(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "squire_state_ledger"
    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    squire_id: Mapped[UUID] = mapped_column(ForeignKey("squires.id", ondelete="RESTRICT"))
    event_id: Mapped[UUID | None] = mapped_column(ForeignKey("events.id", ondelete="SET NULL"))
    effective_year: Mapped[int] = mapped_column(SmallInteger)
    sequence: Mapped[int] = mapped_column(Integer, default=0)
    category: Mapped[str | None] = mapped_column(Text)
    age: Mapped[int] = mapped_column(Integer)
    skill: Mapped[int] = mapped_column(Integer)
    knight_modifier: Mapped[int] = mapped_column(Integer, default=0)
    glory: Mapped[int] = mapped_column(Integer, default=0)
    description: Mapped[str | None] = mapped_column(Text)
    gm_description: Mapped[str | None] = mapped_column(Text)
    reason: Mapped[str | None] = mapped_column(Text)
    recorded_at: Mapped[datetime] = mapped_column(server_default=func.now())
