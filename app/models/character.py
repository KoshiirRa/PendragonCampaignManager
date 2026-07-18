from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from sqlalchemy import Enum, ForeignKey, Integer, SmallInteger, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class CharacterKind(StrEnum):
    PLAYER_KNIGHT = "player_knight"
    NPC = "npc"


class CharacterStatus(StrEnum):
    ALIVE = "alive"
    DEAD = "dead"
    MISSING = "missing"
    UNKNOWN = "unknown"


class KnowledgeScope(StrEnum):
    GM_ONLY = "gm_only"
    PLAYERS = "players"
    SHARED = "shared"


class Character(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "characters"

    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    kind: Mapped[CharacterKind] = mapped_column(
        Enum(
            CharacterKind,
            name="character_kind",
            values_callable=lambda items: [x.value for x in items],
        )
    )
    name: Mapped[str] = mapped_column(Text)
    epithet: Mapped[str | None] = mapped_column(Text)
    player_name: Mapped[str | None] = mapped_column(Text)
    gender: Mapped[str | None] = mapped_column(Text)
    culture: Mapped[str | None] = mapped_column(Text)
    religion: Mapped[str | None] = mapped_column(Text)
    social_class: Mapped[str | None] = mapped_column(Text)
    birth_year: Mapped[int | None] = mapped_column(SmallInteger)
    status: Mapped[CharacterStatus] = mapped_column(
        Enum(
            CharacterStatus,
            name="character_status",
            values_callable=lambda items: [x.value for x in items],
        ),
        default=CharacterStatus.ALIVE,
    )
    coat_of_arms: Mapped[str | None] = mapped_column(Text)
    public_description: Mapped[str | None] = mapped_column(Text)
    foundry_uuid: Mapped[str | None] = mapped_column(Text)
    metadata_: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, default=dict)
    archived_at: Mapped[datetime | None]


class CharacterNote(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "character_notes"

    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    character_id: Mapped[UUID] = mapped_column(ForeignKey("characters.id", ondelete="RESTRICT"))
    event_id: Mapped[UUID | None] = mapped_column(ForeignKey("events.id", ondelete="SET NULL"))
    session_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("campaign_sessions.id", ondelete="SET NULL")
    )
    scope: Mapped[KnowledgeScope] = mapped_column(
        Enum(
            KnowledgeScope,
            name="knowledge_scope",
            values_callable=lambda items: [x.value for x in items],
        ),
        default=KnowledgeScope.GM_ONLY,
    )
    note_type: Mapped[str] = mapped_column(Text, default="general")
    title: Mapped[str | None] = mapped_column(Text)
    body: Mapped[str] = mapped_column(Text)
    recorded_at: Mapped[datetime] = mapped_column(server_default=func.now())


class CharacterStatusLedger(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "character_status_ledger"

    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    character_id: Mapped[UUID] = mapped_column(ForeignKey("characters.id", ondelete="RESTRICT"))
    event_id: Mapped[UUID | None] = mapped_column(ForeignKey("events.id", ondelete="SET NULL"))
    session_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("campaign_sessions.id", ondelete="SET NULL")
    )
    status: Mapped[CharacterStatus] = mapped_column(
        Enum(
            CharacterStatus,
            name="character_status",
            values_callable=lambda items: [x.value for x in items],
        )
    )
    effective_year: Mapped[int] = mapped_column(SmallInteger)
    sequence: Mapped[int] = mapped_column(Integer, default=0)
    reason: Mapped[str | None] = mapped_column(Text)
    recorded_at: Mapped[datetime] = mapped_column(server_default=func.now())


class TraitDefinition(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "trait_definitions"
    __table_args__ = (UniqueConstraint("campaign_id", "name"),)

    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    name: Mapped[str] = mapped_column(Text)
    opposed_name: Mapped[str] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    source_key: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class CharacterTraitLedger(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "character_trait_ledger"

    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    character_id: Mapped[UUID] = mapped_column(ForeignKey("characters.id", ondelete="RESTRICT"))
    trait_definition_id: Mapped[UUID] = mapped_column(
        ForeignKey("trait_definitions.id", ondelete="RESTRICT")
    )
    event_id: Mapped[UUID | None] = mapped_column(ForeignKey("events.id", ondelete="SET NULL"))
    session_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("campaign_sessions.id", ondelete="SET NULL")
    )
    effective_year: Mapped[int] = mapped_column(SmallInteger)
    sequence: Mapped[int] = mapped_column(Integer, default=0)
    trait_value: Mapped[int] = mapped_column(SmallInteger)
    opposed_value: Mapped[int] = mapped_column(SmallInteger)
    reason: Mapped[str | None] = mapped_column(Text)
    recorded_at: Mapped[datetime] = mapped_column(server_default=func.now())


class SkillDefinition(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "skill_definitions"
    __table_args__ = (UniqueConstraint("campaign_id", "name"),)

    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    name: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(Text, default="ordinary")
    description: Mapped[str | None] = mapped_column(Text)
    source_key: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class CharacterSkillLedger(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "character_skill_ledger"

    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    character_id: Mapped[UUID] = mapped_column(ForeignKey("characters.id", ondelete="RESTRICT"))
    skill_definition_id: Mapped[UUID] = mapped_column(
        ForeignKey("skill_definitions.id", ondelete="RESTRICT")
    )
    event_id: Mapped[UUID | None] = mapped_column(ForeignKey("events.id", ondelete="SET NULL"))
    session_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("campaign_sessions.id", ondelete="SET NULL")
    )
    effective_year: Mapped[int] = mapped_column(SmallInteger)
    sequence: Mapped[int] = mapped_column(Integer, default=0)
    value: Mapped[int] = mapped_column(SmallInteger)
    reason: Mapped[str | None] = mapped_column(Text)
    recorded_at: Mapped[datetime] = mapped_column(server_default=func.now())


class CharacterPassion(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "character_passions"

    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    character_id: Mapped[UUID] = mapped_column(ForeignKey("characters.id", ondelete="RESTRICT"))
    name: Mapped[str] = mapped_column(Text)
    subject_text: Mapped[str | None] = mapped_column(Text)
    source_key: Mapped[str | None] = mapped_column(Text)
    related_character_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("characters.id", ondelete="RESTRICT")
    )
    scope: Mapped[KnowledgeScope] = mapped_column(
        Enum(
            KnowledgeScope,
            name="knowledge_scope",
            values_callable=lambda items: [x.value for x in items],
        )
    )
    started_event_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("events.id", ondelete="SET NULL")
    )
    ended_event_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("events.id", ondelete="SET NULL")
    )
    started_year: Mapped[int | None] = mapped_column(SmallInteger)
    ended_year: Mapped[int | None] = mapped_column(SmallInteger)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class CharacterPassionLedger(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "character_passion_ledger"

    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    passion_id: Mapped[UUID] = mapped_column(
        ForeignKey("character_passions.id", ondelete="RESTRICT")
    )
    event_id: Mapped[UUID | None] = mapped_column(ForeignKey("events.id", ondelete="SET NULL"))
    session_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("campaign_sessions.id", ondelete="SET NULL")
    )
    effective_year: Mapped[int] = mapped_column(SmallInteger)
    sequence: Mapped[int] = mapped_column(Integer, default=0)
    value: Mapped[int] = mapped_column(SmallInteger)
    reason: Mapped[str | None] = mapped_column(Text)
    recorded_at: Mapped[datetime] = mapped_column(server_default=func.now())


class GloryLedger(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "glory_ledger"

    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    character_id: Mapped[UUID] = mapped_column(ForeignKey("characters.id", ondelete="RESTRICT"))
    event_id: Mapped[UUID | None] = mapped_column(ForeignKey("events.id", ondelete="SET NULL"))
    session_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("campaign_sessions.id", ondelete="SET NULL")
    )
    awarded_year: Mapped[int] = mapped_column(SmallInteger)
    sequence: Mapped[int] = mapped_column(Integer, default=0)
    amount: Mapped[int] = mapped_column(Integer)
    category: Mapped[str] = mapped_column(Text, default="other")
    reason: Mapped[str] = mapped_column(Text)
    scope: Mapped[KnowledgeScope] = mapped_column(
        Enum(
            KnowledgeScope,
            name="knowledge_scope",
            values_callable=lambda items: [x.value for x in items],
        )
    )
    recorded_at: Mapped[datetime] = mapped_column(server_default=func.now())
