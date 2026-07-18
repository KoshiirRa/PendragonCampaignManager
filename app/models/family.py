from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import Boolean, Enum, ForeignKey, SmallInteger, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.character import KnowledgeScope


class Family(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "families"

    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    name: Mapped[str] = mapped_column(Text)
    founding_year: Mapped[int | None] = mapped_column(SmallInteger)
    dissolved_year: Mapped[int | None] = mapped_column(SmallInteger)
    origin_location_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("locations.id", ondelete="RESTRICT")
    )
    culture: Mapped[str | None] = mapped_column(Text)
    religion: Mapped[str | None] = mapped_column(Text)
    coat_of_arms: Mapped[str | None] = mapped_column(Text)
    motto: Mapped[str | None] = mapped_column(Text)
    scope: Mapped[KnowledgeScope] = mapped_column(
        Enum(
            KnowledgeScope,
            name="knowledge_scope",
            values_callable=lambda items: [x.value for x in items],
        )
    )
    notes: Mapped[str | None] = mapped_column(Text)
    metadata_: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, default=dict)
    archived_at: Mapped[datetime | None]


class FamilyMembership(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "family_memberships"

    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    source_key: Mapped[str | None] = mapped_column(Text)
    family_id: Mapped[UUID] = mapped_column(ForeignKey("families.id", ondelete="RESTRICT"))
    character_id: Mapped[UUID] = mapped_column(ForeignKey("characters.id", ondelete="RESTRICT"))
    membership_type: Mapped[str] = mapped_column(Text, default="birth")
    branch_name: Mapped[str | None] = mapped_column(Text)
    start_year: Mapped[int | None] = mapped_column(SmallInteger)
    end_year: Mapped[int | None] = mapped_column(SmallInteger)
    start_event_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("events.id", ondelete="SET NULL")
    )
    end_event_id: Mapped[UUID | None] = mapped_column(ForeignKey("events.id", ondelete="SET NULL"))
    is_primary: Mapped[bool] = mapped_column(Boolean, default=True)
    scope: Mapped[KnowledgeScope] = mapped_column(
        Enum(
            KnowledgeScope,
            name="knowledge_scope",
            values_callable=lambda items: [x.value for x in items],
        )
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class CharacterParentage(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "character_parentage"
    __table_args__ = (
        UniqueConstraint("parent_character_id", "child_character_id", "relationship_type"),
    )

    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    source_key: Mapped[str | None] = mapped_column(Text)
    parent_character_id: Mapped[UUID] = mapped_column(
        ForeignKey("characters.id", ondelete="RESTRICT")
    )
    child_character_id: Mapped[UUID] = mapped_column(
        ForeignKey("characters.id", ondelete="RESTRICT")
    )
    relationship_type: Mapped[str] = mapped_column(Text, default="biological")
    certainty: Mapped[str] = mapped_column(Text, default="confirmed")
    event_id: Mapped[UUID | None] = mapped_column(ForeignKey("events.id", ondelete="SET NULL"))
    scope: Mapped[KnowledgeScope] = mapped_column(
        Enum(
            KnowledgeScope,
            name="knowledge_scope",
            values_callable=lambda items: [x.value for x in items],
        )
    )
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class Marriage(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "marriages"

    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    source_key: Mapped[str | None] = mapped_column(Text)
    spouse_one_id: Mapped[UUID] = mapped_column(ForeignKey("characters.id", ondelete="RESTRICT"))
    spouse_two_id: Mapped[UUID] = mapped_column(ForeignKey("characters.id", ondelete="RESTRICT"))
    start_event_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("events.id", ondelete="SET NULL")
    )
    end_event_id: Mapped[UUID | None] = mapped_column(ForeignKey("events.id", ondelete="SET NULL"))
    start_year: Mapped[int] = mapped_column(SmallInteger)
    end_year: Mapped[int | None] = mapped_column(SmallInteger)
    end_reason: Mapped[str | None] = mapped_column(Text)
    scope: Mapped[KnowledgeScope] = mapped_column(
        Enum(
            KnowledgeScope,
            name="knowledge_scope",
            values_callable=lambda items: [x.value for x in items],
        )
    )
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class InheritanceCase(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "inheritance_cases"

    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    source_key: Mapped[str | None] = mapped_column(Text)
    decedent_character_id: Mapped[UUID] = mapped_column(
        ForeignKey("characters.id", ondelete="RESTRICT")
    )
    opened_event_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("events.id", ondelete="SET NULL")
    )
    settled_event_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("events.id", ondelete="SET NULL")
    )
    opened_year: Mapped[int] = mapped_column(SmallInteger)
    settled_year: Mapped[int | None] = mapped_column(SmallInteger)
    governing_custom: Mapped[str | None] = mapped_column(Text)
    will_summary: Mapped[str | None] = mapped_column(Text)
    scope: Mapped[KnowledgeScope] = mapped_column(
        Enum(
            KnowledgeScope,
            name="knowledge_scope",
            values_callable=lambda items: [x.value for x in items],
        )
    )
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class InheritanceHeir(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "inheritance_heirs"
    __table_args__ = (UniqueConstraint("inheritance_case_id", "character_id"),)

    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    source_key: Mapped[str | None] = mapped_column(Text)
    inheritance_case_id: Mapped[UUID] = mapped_column(
        ForeignKey("inheritance_cases.id", ondelete="RESTRICT")
    )
    character_id: Mapped[UUID] = mapped_column(ForeignKey("characters.id", ondelete="RESTRICT"))
    priority: Mapped[int | None] = mapped_column(SmallInteger)
    relationship_description: Mapped[str | None] = mapped_column(Text)
    claim_status: Mapped[str] = mapped_column(Text, default="potential")
    designated: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class InheritanceManorTransfer(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "inheritance_manor_transfers"
    __table_args__ = (UniqueConstraint("inheritance_case_id", "manor_id"),)

    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    inheritance_case_id: Mapped[UUID] = mapped_column(
        ForeignKey("inheritance_cases.id", ondelete="RESTRICT")
    )
    manor_id: Mapped[UUID] = mapped_column(ForeignKey("manors.id", ondelete="RESTRICT"))
    beneficiary_character_id: Mapped[UUID] = mapped_column(
        ForeignKey("characters.id", ondelete="RESTRICT")
    )
    event_id: Mapped[UUID] = mapped_column(ForeignKey("events.id", ondelete="RESTRICT"))
    transferred_year: Mapped[int] = mapped_column(SmallInteger)
    terms: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class SourceReference(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "source_references"
    __table_args__ = (UniqueConstraint("campaign_id", "title", "edition"),)

    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    source_type: Mapped[str] = mapped_column(Text, default="book")
    title: Mapped[str] = mapped_column(Text)
    edition: Mapped[str | None] = mapped_column(Text)
    publication_year: Mapped[int | None] = mapped_column(SmallInteger)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class FamilyHistoryEntry(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "family_history_entries"

    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    family_id: Mapped[UUID] = mapped_column(ForeignKey("families.id", ondelete="RESTRICT"))
    ancestor_character_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("characters.id", ondelete="RESTRICT")
    )
    event_id: Mapped[UUID] = mapped_column(
        ForeignKey("events.id", ondelete="RESTRICT"), unique=True
    )
    realm_location_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("locations.id", ondelete="RESTRICT")
    )
    source_reference_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("source_references.id", ondelete="RESTRICT")
    )
    dice_log_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("dice_logs.id", ondelete="SET NULL")
    )
    glory_ledger_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("glory_ledger.id", ondelete="SET NULL"), unique=True
    )
    start_year: Mapped[int] = mapped_column(SmallInteger)
    end_year: Mapped[int | None] = mapped_column(SmallInteger)
    entry_type: Mapped[str] = mapped_column(Text, default="annual_service")
    title: Mapped[str] = mapped_column(Text)
    summary: Mapped[str] = mapped_column(Text)
    generation_method: Mapped[str] = mapped_column(Text, default="manual")
    source_locator: Mapped[str | None] = mapped_column(Text)
    roll_expression: Mapped[str | None] = mapped_column(Text)
    roll_result: Mapped[str | None] = mapped_column(Text)
    scope: Mapped[KnowledgeScope] = mapped_column(
        Enum(
            KnowledgeScope,
            name="knowledge_scope",
            values_callable=lambda items: [x.value for x in items],
        )
    )
    metadata_: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
