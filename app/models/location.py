from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any
from uuid import UUID

from sqlalchemy import Enum, ForeignKey, Integer, Numeric, SmallInteger, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.character import KnowledgeScope


class LocationKind(StrEnum):
    KINGDOM = "kingdom"
    COUNTY = "county"
    BARONY = "barony"
    MANOR = "manor"
    HOLDING = "holding"
    SETTLEMENT = "settlement"
    CASTLE = "castle"
    CHURCH = "church"
    FOREST = "forest"
    ROAD = "road"
    OTHER = "other"


class Location(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "locations"

    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    parent_location_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("locations.id", ondelete="RESTRICT")
    )
    kind: Mapped[LocationKind] = mapped_column(
        Enum(
            LocationKind,
            name="location_kind",
            values_callable=lambda items: [x.value for x in items],
        )
    )
    name: Mapped[str] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    scope: Mapped[KnowledgeScope] = mapped_column(
        Enum(
            KnowledgeScope,
            name="knowledge_scope",
            values_callable=lambda items: [x.value for x in items],
        )
    )
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    metadata_: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, default=dict)
    archived_at: Mapped[datetime | None]


class LocationConnection(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "location_connections"

    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    from_location_id: Mapped[UUID] = mapped_column(ForeignKey("locations.id", ondelete="RESTRICT"))
    to_location_id: Mapped[UUID] = mapped_column(ForeignKey("locations.id", ondelete="RESTRICT"))
    relationship_type: Mapped[str] = mapped_column(Text, default="route")
    distance_miles: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime]


class Manor(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "manors"

    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    location_id: Mapped[UUID] = mapped_column(
        ForeignKey("locations.id", ondelete="RESTRICT"), unique=True
    )
    customary_income: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    acreage: Mapped[int | None] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(Text)


class ManorTenure(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "manor_tenures"

    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    manor_id: Mapped[UUID] = mapped_column(ForeignKey("manors.id", ondelete="RESTRICT"))
    holder_character_id: Mapped[UUID] = mapped_column(
        ForeignKey("characters.id", ondelete="RESTRICT")
    )
    liege_character_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("characters.id", ondelete="RESTRICT")
    )
    start_event_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("events.id", ondelete="SET NULL")
    )
    end_event_id: Mapped[UUID | None] = mapped_column(ForeignKey("events.id", ondelete="SET NULL"))
    start_year: Mapped[int] = mapped_column(SmallInteger)
    end_year: Mapped[int | None] = mapped_column(SmallInteger)
    tenure_type: Mapped[str] = mapped_column(Text, default="grant")
    terms: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime]


class ManorImprovement(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "manor_improvements"

    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    manor_id: Mapped[UUID] = mapped_column(ForeignKey("manors.id", ondelete="RESTRICT"))
    name: Mapped[str] = mapped_column(Text)
    improvement_type: Mapped[str] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime]


class ManorImprovementLedger(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "manor_improvement_ledger"

    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    improvement_id: Mapped[UUID] = mapped_column(
        ForeignKey("manor_improvements.id", ondelete="RESTRICT")
    )
    event_id: Mapped[UUID | None] = mapped_column(ForeignKey("events.id", ondelete="SET NULL"))
    effective_year: Mapped[int] = mapped_column(SmallInteger)
    status: Mapped[str] = mapped_column(Text)
    income_modifier: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"))
    maintenance_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"))
    notes: Mapped[str | None] = mapped_column(Text)
    recorded_at: Mapped[datetime]
