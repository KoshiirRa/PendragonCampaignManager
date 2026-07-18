from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Integer, SmallInteger, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKeyMixin


class CharacterHistoryEntry(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "character_history_entries"
    __table_args__ = (UniqueConstraint("campaign_id", "source_key"),)

    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    character_id: Mapped[UUID] = mapped_column(ForeignKey("characters.id", ondelete="RESTRICT"))
    event_id: Mapped[UUID] = mapped_column(ForeignKey("events.id", ondelete="RESTRICT"))
    source_key: Mapped[str] = mapped_column(Text)
    in_game_year: Mapped[int] = mapped_column(SmallInteger)
    title: Mapped[str] = mapped_column(Text)
    source: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    reported_glory: Mapped[int] = mapped_column(Integer, default=0)
    favour_value: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class WinterPhase(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "winter_phases"
    __table_args__ = (UniqueConstraint("campaign_id", "in_game_year"),)

    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    event_id: Mapped[UUID] = mapped_column(ForeignKey("events.id", ondelete="RESTRICT"))
    in_game_year: Mapped[int] = mapped_column(SmallInteger)
    status: Mapped[str] = mapped_column(Text, default="recorded")
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class WinterPhaseParticipant(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "winter_phase_participants"
    __table_args__ = (UniqueConstraint("winter_phase_id", "character_id"),)

    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    winter_phase_id: Mapped[UUID] = mapped_column(
        ForeignKey("winter_phases.id", ondelete="RESTRICT")
    )
    character_id: Mapped[UUID] = mapped_column(ForeignKey("characters.id", ondelete="RESTRICT"))
    history_entry_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("character_history_entries.id", ondelete="RESTRICT")
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class CharacterWoundLedger(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "character_wound_ledger"

    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    character_id: Mapped[UUID] = mapped_column(ForeignKey("characters.id", ondelete="RESTRICT"))
    event_id: Mapped[UUID | None] = mapped_column(ForeignKey("events.id", ondelete="SET NULL"))
    source_key: Mapped[str] = mapped_column(Text)
    effective_year: Mapped[int] = mapped_column(SmallInteger)
    sequence: Mapped[int] = mapped_column(SmallInteger, default=0)
    damage: Mapped[int] = mapped_column(Integer)
    treated: Mapped[bool] = mapped_column(Boolean, default=False)
    wound_source: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    reason: Mapped[str | None] = mapped_column(Text)
    recorded_at: Mapped[datetime] = mapped_column(server_default=func.now())


class AnnualChronicle(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "annual_chronicles"
    __table_args__ = (UniqueConstraint("campaign_id", "in_game_year", "revision"),)

    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    winter_phase_id: Mapped[UUID] = mapped_column(
        ForeignKey("winter_phases.id", ondelete="RESTRICT")
    )
    in_game_year: Mapped[int] = mapped_column(SmallInteger)
    revision: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(Text)
    opening: Mapped[str] = mapped_column(Text)
    closing: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, default="published")
    generator_version: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class AnnualChronicleSection(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "annual_chronicle_sections"
    __table_args__ = (
        UniqueConstraint("chronicle_id", "character_id"),
        UniqueConstraint("chronicle_id", "position"),
    )

    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    chronicle_id: Mapped[UUID] = mapped_column(
        ForeignKey("annual_chronicles.id", ondelete="RESTRICT")
    )
    character_id: Mapped[UUID] = mapped_column(ForeignKey("characters.id", ondelete="RESTRICT"))
    position: Mapped[int] = mapped_column(Integer)
    heading: Mapped[str] = mapped_column(Text)
    body: Mapped[str] = mapped_column(Text)


class AnnualChronicleSource(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "annual_chronicle_sources"
    __table_args__ = (UniqueConstraint("chronicle_id", "section_id", "event_id"),)

    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    chronicle_id: Mapped[UUID] = mapped_column(
        ForeignKey("annual_chronicles.id", ondelete="RESTRICT")
    )
    section_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("annual_chronicle_sections.id", ondelete="RESTRICT")
    )
    event_id: Mapped[UUID] = mapped_column(ForeignKey("events.id", ondelete="RESTRICT"))
