from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Integer, SmallInteger, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKeyMixin


class CharacterStatLedger(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "character_stat_ledger"
    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    character_id: Mapped[UUID] = mapped_column(ForeignKey("characters.id", ondelete="RESTRICT"))
    event_id: Mapped[UUID | None] = mapped_column(ForeignKey("events.id", ondelete="SET NULL"))
    stat_code: Mapped[str] = mapped_column(Text)
    effective_year: Mapped[int] = mapped_column(SmallInteger)
    sequence: Mapped[int] = mapped_column(Integer, default=0)
    value: Mapped[int] = mapped_column(SmallInteger)
    reason: Mapped[str | None] = mapped_column(Text)
    recorded_at: Mapped[datetime] = mapped_column(server_default=func.now())


class InventoryItem(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "inventory_items"
    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    source_key: Mapped[str] = mapped_column(Text)
    item_type: Mapped[str] = mapped_column(Text)
    name: Mapped[str] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    libra: Mapped[int] = mapped_column(Integer, default=0)
    denarii: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class WeaponProfile(Base):
    __tablename__ = "weapon_profiles"
    inventory_item_id: Mapped[UUID] = mapped_column(
        ForeignKey("inventory_items.id", ondelete="RESTRICT"), primary_key=True
    )
    skill: Mapped[str | None] = mapped_column(Text)
    damage_formula: Mapped[str | None] = mapped_column(Text)
    weapon_range: Mapped[str | None] = mapped_column(Text)
    mounted_use: Mapped[str | None] = mapped_column(Text)
    melee: Mapped[bool] = mapped_column(Boolean, default=True)


class ArmourProfile(Base):
    __tablename__ = "armour_profiles"
    inventory_item_id: Mapped[UUID] = mapped_column(
        ForeignKey("inventory_items.id", ondelete="RESTRICT"), primary_key=True
    )
    armour_points: Mapped[int] = mapped_column(SmallInteger, default=0)
    material: Mapped[str | None] = mapped_column(Text)
    is_shield: Mapped[bool] = mapped_column(Boolean, default=False)


class CharacterInventoryLedger(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "character_inventory_ledger"
    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    character_id: Mapped[UUID] = mapped_column(ForeignKey("characters.id", ondelete="RESTRICT"))
    inventory_item_id: Mapped[UUID] = mapped_column(
        ForeignKey("inventory_items.id", ondelete="RESTRICT")
    )
    event_id: Mapped[UUID | None] = mapped_column(ForeignKey("events.id", ondelete="SET NULL"))
    effective_year: Mapped[int] = mapped_column(SmallInteger)
    sequence: Mapped[int] = mapped_column(Integer, default=0)
    quantity: Mapped[int] = mapped_column(Integer)
    equipped: Mapped[bool] = mapped_column(Boolean, default=False)
    reason: Mapped[str | None] = mapped_column(Text)
    recorded_at: Mapped[datetime] = mapped_column(server_default=func.now())


class Horse(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "horses"
    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    source_key: Mapped[str] = mapped_column(Text)
    name: Mapped[str] = mapped_column(Text)
    breed: Mapped[str | None] = mapped_column(Text)
    colour: Mapped[str | None] = mapped_column(Text)
    personality: Mapped[str | None] = mapped_column(Text)
    features: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class HorseOwnershipHistory(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "horse_ownership_history"
    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    horse_id: Mapped[UUID] = mapped_column(ForeignKey("horses.id", ondelete="RESTRICT"))
    character_id: Mapped[UUID] = mapped_column(ForeignKey("characters.id", ondelete="RESTRICT"))
    start_event_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("events.id", ondelete="SET NULL")
    )
    end_event_id: Mapped[UUID | None] = mapped_column(ForeignKey("events.id", ondelete="SET NULL"))
    start_year: Mapped[int] = mapped_column(SmallInteger)
    end_year: Mapped[int | None] = mapped_column(SmallInteger)


class HorseStatLedger(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "horse_stat_ledger"
    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"))
    horse_id: Mapped[UUID] = mapped_column(ForeignKey("horses.id", ondelete="RESTRICT"))
    event_id: Mapped[UUID | None] = mapped_column(ForeignKey("events.id", ondelete="SET NULL"))
    effective_year: Mapped[int] = mapped_column(SmallInteger)
    sequence: Mapped[int] = mapped_column(Integer, default=0)
    siz: Mapped[int] = mapped_column(SmallInteger, default=0)
    dex: Mapped[int] = mapped_column(SmallInteger, default=0)
    str: Mapped[int] = mapped_column(SmallInteger, default=0)
    con: Mapped[int] = mapped_column(SmallInteger, default=0)
    hp: Mapped[int] = mapped_column(SmallInteger, default=0)
    max_hp: Mapped[int] = mapped_column(SmallInteger, default=0)
    move: Mapped[int] = mapped_column(SmallInteger, default=0)
    armour: Mapped[int] = mapped_column(SmallInteger, default=0)
    horse_armour: Mapped[int] = mapped_column(SmallInteger, default=0)
    age: Mapped[int] = mapped_column(SmallInteger, default=0)
    equipped: Mapped[bool] = mapped_column(Boolean, default=False)
    reason: Mapped[str | None] = mapped_column(Text)
    recorded_at: Mapped[datetime] = mapped_column(server_default=func.now())
