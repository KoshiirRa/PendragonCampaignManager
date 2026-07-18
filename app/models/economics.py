from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, Numeric, SmallInteger, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKeyMixin


class ManorAnnualResolution(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "manor_annual_resolutions"
    __table_args__ = (UniqueConstraint("manor_id", "in_game_year"),)

    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    manor_id: Mapped[UUID] = mapped_column(ForeignKey("manors.id", ondelete="RESTRICT"))
    event_id: Mapped[UUID] = mapped_column(ForeignKey("events.id", ondelete="RESTRICT"))
    winter_phase_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("winter_phases.id", ondelete="RESTRICT")
    )
    in_game_year: Mapped[int] = mapped_column(SmallInteger)
    steward_character_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("characters.id", ondelete="RESTRICT")
    )
    stewardship_value: Mapped[int | None] = mapped_column(Integer)
    roll_result: Mapped[str] = mapped_column(Text)
    income: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"))
    expenses: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"))
    privy_funds: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"))
    famine_stage: Mapped[int] = mapped_column(SmallInteger, default=0)
    population_change: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class ManorTreasuryEntry(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "manor_treasury_ledger"
    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    manor_id: Mapped[UUID] = mapped_column(ForeignKey("manors.id", ondelete="RESTRICT"))
    event_id: Mapped[UUID | None] = mapped_column(ForeignKey("events.id", ondelete="SET NULL"))
    annual_resolution_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("manor_annual_resolutions.id", ondelete="RESTRICT")
    )
    in_game_year: Mapped[int] = mapped_column(SmallInteger)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    category: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class ManorAsset(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "manor_assets"
    __table_args__ = (UniqueConstraint("manor_id", "asset_type", "name"),)
    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    manor_id: Mapped[UUID] = mapped_column(ForeignKey("manors.id", ondelete="RESTRICT"))
    asset_type: Mapped[str] = mapped_column(Text)
    name: Mapped[str] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class ManorAssetLedger(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "manor_asset_ledger"
    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    asset_id: Mapped[UUID] = mapped_column(ForeignKey("manor_assets.id", ondelete="RESTRICT"))
    event_id: Mapped[UUID | None] = mapped_column(ForeignKey("events.id", ondelete="SET NULL"))
    effective_year: Mapped[int] = mapped_column(SmallInteger)
    quantity: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    status: Mapped[str] = mapped_column(Text)
    annual_income: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"))
    annual_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"))
    notes: Mapped[str | None] = mapped_column(Text)
    recorded_at: Mapped[datetime] = mapped_column(server_default=func.now())


class HouseholdEmployment(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "household_employment_history"
    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    manor_id: Mapped[UUID] = mapped_column(ForeignKey("manors.id", ondelete="RESTRICT"))
    character_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("characters.id", ondelete="RESTRICT")
    )
    name: Mapped[str] = mapped_column(Text)
    role: Mapped[str] = mapped_column(Text)
    social_rank: Mapped[str | None] = mapped_column(Text)
    key_skill: Mapped[str | None] = mapped_column(Text)
    key_skill_value: Mapped[int | None] = mapped_column(Integer)
    annual_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"))
    start_year: Mapped[int] = mapped_column(SmallInteger)
    end_year: Mapped[int | None] = mapped_column(SmallInteger)
    start_event_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("events.id", ondelete="SET NULL")
    )
    end_event_id: Mapped[UUID | None] = mapped_column(ForeignKey("events.id", ondelete="SET NULL"))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class ManorDefenseLayer(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "manor_defense_layers"
    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    manor_id: Mapped[UUID] = mapped_column(ForeignKey("manors.id", ondelete="RESTRICT"))
    name: Mapped[str] = mapped_column(Text)
    ring_order: Mapped[int] = mapped_column(SmallInteger)
    defensive_value: Mapped[int] = mapped_column(Integer)
    construction_cost: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    improvement_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("manor_improvements.id", ondelete="RESTRICT")
    )
