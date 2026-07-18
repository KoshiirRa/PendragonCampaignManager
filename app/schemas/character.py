from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import Field, model_validator

from app.schemas.common import ORMModel

KnowledgeScopeValue = Literal["gm_only", "players", "shared"]


class CharacterCreate(ORMModel):
    kind: Literal["player_knight", "npc"]
    name: str = Field(min_length=1, max_length=300)
    epithet: str | None = None
    player_name: str | None = None
    gender: str | None = None
    culture: str | None = None
    religion: str | None = None
    social_class: str | None = None
    birth_year: int | None = Field(default=None, ge=1, le=9999)
    status: Literal["alive", "dead", "missing", "unknown"] = "alive"
    coat_of_arms: str | None = None
    public_description: str | None = None
    foundry_uuid: str | None = Field(default=None, max_length=500)
    metadata: dict[str, Any] = Field(
        default_factory=dict, validation_alias="metadata_", serialization_alias="metadata"
    )

    @model_validator(mode="after")
    def player_knight_has_player(self) -> "CharacterCreate":
        if self.kind == "player_knight" and not (self.player_name and self.player_name.strip()):
            raise ValueError("player_name is required for a player knight")
        return self


class CharacterUpdate(ORMModel):
    name: str | None = Field(default=None, min_length=1, max_length=300)
    epithet: str | None = None
    player_name: str | None = None
    gender: str | None = None
    culture: str | None = None
    religion: str | None = None
    social_class: str | None = None
    birth_year: int | None = Field(default=None, ge=1, le=9999)
    coat_of_arms: str | None = None
    public_description: str | None = None
    foundry_uuid: str | None = Field(default=None, max_length=500)
    metadata: dict[str, Any] | None = None


class CharacterRead(CharacterCreate):
    id: UUID
    campaign_id: UUID
    archived_at: datetime | None
    created_at: datetime
    updated_at: datetime


class CharacterNoteCreate(ORMModel):
    event_id: UUID | None = None
    session_id: UUID | None = None
    scope: KnowledgeScopeValue = "gm_only"
    note_type: str = Field(default="general", min_length=1, max_length=100)
    title: str | None = Field(default=None, max_length=300)
    body: str = Field(min_length=1)


class CharacterNoteRead(CharacterNoteCreate):
    id: UUID
    campaign_id: UUID
    character_id: UUID
    recorded_at: datetime


class CharacterStatusCreate(ORMModel):
    event_id: UUID | None = None
    session_id: UUID | None = None
    status: Literal["alive", "dead", "missing", "unknown"]
    effective_year: int = Field(ge=1, le=9999)
    sequence: int = Field(default=0, ge=0)
    reason: str | None = None


class CharacterStatusRead(CharacterStatusCreate):
    id: UUID
    campaign_id: UUID
    character_id: UUID
    recorded_at: datetime


class TraitDefinitionCreate(ORMModel):
    name: str = Field(min_length=1, max_length=100)
    opposed_name: str = Field(min_length=1, max_length=100)
    description: str | None = None


class TraitDefinitionRead(TraitDefinitionCreate):
    id: UUID
    campaign_id: UUID
    created_at: datetime


class TraitLedgerCreate(ORMModel):
    trait_definition_id: UUID
    event_id: UUID | None = None
    session_id: UUID | None = None
    effective_year: int = Field(ge=1, le=9999)
    sequence: int = Field(default=0, ge=0)
    trait_value: int = Field(ge=0)
    opposed_value: int = Field(ge=0)
    reason: str | None = None


class TraitLedgerRead(TraitLedgerCreate):
    id: UUID
    campaign_id: UUID
    character_id: UUID
    recorded_at: datetime


class SkillDefinitionCreate(ORMModel):
    name: str = Field(min_length=1, max_length=100)
    category: str = Field(default="ordinary", min_length=1, max_length=100)
    description: str | None = None


class SkillDefinitionRead(SkillDefinitionCreate):
    id: UUID
    campaign_id: UUID
    created_at: datetime


class SkillLedgerCreate(ORMModel):
    skill_definition_id: UUID
    event_id: UUID | None = None
    session_id: UUID | None = None
    effective_year: int = Field(ge=1, le=9999)
    sequence: int = Field(default=0, ge=0)
    value: int = Field(ge=0)
    reason: str | None = None


class SkillLedgerRead(SkillLedgerCreate):
    id: UUID
    campaign_id: UUID
    character_id: UUID
    recorded_at: datetime


class PassionCreate(ORMModel):
    name: str = Field(min_length=1, max_length=150)
    subject_text: str | None = None
    related_character_id: UUID | None = None
    scope: KnowledgeScopeValue = "players"
    started_event_id: UUID | None = None
    started_year: int | None = Field(default=None, ge=1, le=9999)


class PassionRead(PassionCreate):
    id: UUID
    campaign_id: UUID
    character_id: UUID
    ended_event_id: UUID | None
    ended_year: int | None
    created_at: datetime


class PassionLedgerCreate(ORMModel):
    event_id: UUID | None = None
    session_id: UUID | None = None
    effective_year: int = Field(ge=1, le=9999)
    sequence: int = Field(default=0, ge=0)
    value: int = Field(ge=0)
    reason: str | None = None


class PassionLedgerRead(PassionLedgerCreate):
    id: UUID
    campaign_id: UUID
    passion_id: UUID
    recorded_at: datetime


class GloryCreate(ORMModel):
    event_id: UUID | None = None
    session_id: UUID | None = None
    awarded_year: int = Field(ge=1, le=9999)
    sequence: int = Field(default=0, ge=0)
    amount: int
    category: str = Field(default="other", min_length=1, max_length=100)
    reason: str = Field(min_length=1)
    scope: KnowledgeScopeValue = "players"

    @model_validator(mode="after")
    def nonzero_amount(self) -> "GloryCreate":
        if self.amount == 0:
            raise ValueError("amount must not be zero")
        return self


class GloryRead(GloryCreate):
    id: UUID
    campaign_id: UUID
    character_id: UUID
    recorded_at: datetime


class GlorySummary(ORMModel):
    character_id: UUID
    total: int
    entries: list[GloryRead]


class FoundryTraitSnapshot(ORMModel):
    source_key: str = Field(min_length=1, max_length=500)
    name: str = Field(min_length=1, max_length=100)
    opposed_name: str = Field(min_length=1, max_length=100)
    value: int = Field(ge=0)
    opposed_value: int = Field(ge=0)


class FoundrySkillSnapshot(ORMModel):
    source_key: str = Field(min_length=1, max_length=500)
    name: str = Field(min_length=1, max_length=100)
    category: str = Field(default="ordinary", min_length=1, max_length=100)
    value: int = Field(ge=0)


class FoundryPassionSnapshot(ORMModel):
    source_key: str = Field(min_length=1, max_length=500)
    name: str = Field(min_length=1, max_length=150)
    subject_text: str | None = Field(default=None, max_length=300)
    value: int = Field(ge=0)


class FoundryStatSnapshot(ORMModel):
    code: Literal["siz", "dex", "str", "con", "app"]
    value: int = Field(ge=0)


class FoundryInventorySnapshot(ORMModel):
    source_key: str = Field(min_length=1, max_length=500)
    item_type: Literal["gear", "weapon", "armour"]
    name: str = Field(min_length=1, max_length=300)
    description: str | None = None
    quantity: int = Field(default=1, ge=0)
    equipped: bool = False
    libra: int = Field(default=0, ge=0)
    denarii: int = Field(default=0, ge=0)
    skill: str | None = None
    damage_formula: str | None = None
    weapon_range: str | None = None
    mounted_use: str | None = None
    melee: bool = True
    armour_points: int = Field(default=0, ge=0)
    material: str | None = None
    is_shield: bool = False


class FoundryHorseSnapshot(ORMModel):
    source_key: str = Field(min_length=1, max_length=500)
    name: str = Field(min_length=1, max_length=300)
    breed: str | None = None
    colour: str | None = None
    personality: str | None = None
    features: str | None = None
    description: str | None = None
    siz: int = Field(default=0, ge=0)
    dex: int = Field(default=0, ge=0)
    str: int = Field(default=0, ge=0)
    con: int = Field(default=0, ge=0)
    hp: int = Field(default=0, ge=0)
    max_hp: int = Field(default=0, ge=0)
    move: int = Field(default=0, ge=0)
    armour: int = Field(default=0, ge=0)
    horse_armour: int = Field(default=0, ge=0)
    age: int = Field(default=0, ge=0)
    equipped: bool = False


class FoundryRelativeSnapshot(ORMModel):
    source_key: str = Field(min_length=1, max_length=500)
    name: str = Field(min_length=1, max_length=300)
    relation: Literal["parent", "spouse", "child", "other"]
    gender: str | None = None
    birth_year: int | None = Field(default=None, ge=1, le=9999)
    death_year: int | None = Field(default=None, ge=1, le=9999)
    glory_total: int = Field(default=0, ge=0)
    blessed_birth: bool = False
    barren_marriage: bool = False
    description: str | None = None
    gm_description: str | None = None

    @model_validator(mode="after")
    def valid_lifespan(self) -> "FoundryRelativeSnapshot":
        if self.birth_year and self.death_year and self.death_year < self.birth_year:
            raise ValueError("death_year cannot precede birth_year")
        return self


class FoundryHistorySnapshot(ORMModel):
    source_key: str = Field(min_length=1, max_length=500)
    year: int = Field(ge=1, le=9999)
    title: str = Field(min_length=1, max_length=300)
    source: str | None = Field(default=None, max_length=100)
    description: str | None = None
    gm_description: str | None = None
    reported_glory: int = 0
    favour_value: int = 0


class FoundryWoundSnapshot(ORMModel):
    source_key: str = Field(min_length=1, max_length=500)
    damage: int = Field(ge=0)
    treated: bool = False
    wound_source: str | None = Field(default=None, max_length=100)
    description: str | None = None


class FoundryCharacterSnapshot(ORMModel):
    effective_year: int = Field(ge=1, le=9999)
    traits: list[FoundryTraitSnapshot] = Field(default_factory=list, max_length=100)
    skills: list[FoundrySkillSnapshot] = Field(default_factory=list, max_length=300)
    passions: list[FoundryPassionSnapshot] = Field(default_factory=list, max_length=100)
    glory_total: int = Field(ge=0)
    stats: list[FoundryStatSnapshot] | None = Field(default=None, max_length=5)
    inventory: list[FoundryInventorySnapshot] | None = Field(default=None, max_length=500)
    horses: list[FoundryHorseSnapshot] | None = Field(default=None, max_length=100)
    family_name: str | None = Field(default=None, min_length=1, max_length=300)
    relatives: list[FoundryRelativeSnapshot] | None = Field(default=None, max_length=500)
    is_heir: bool = False
    history: list[FoundryHistorySnapshot] | None = Field(default=None, max_length=1000)
    wounds: list[FoundryWoundSnapshot] | None = Field(default=None, max_length=100)

    @model_validator(mode="after")
    def unique_source_keys(self) -> "FoundryCharacterSnapshot":
        stat_codes = [stat.code for stat in self.stats or []]
        if len(stat_codes) != len(set(stat_codes)):
            raise ValueError("duplicate statistic code")
        for label, values in (
            ("trait", self.traits),
            ("skill", self.skills),
            ("passion", self.passions),
            ("inventory", self.inventory or []),
            ("horse", self.horses or []),
            ("relative", self.relatives or []),
            ("history", self.history or []),
            ("wound", self.wounds or []),
        ):
            keys = [value.source_key for value in values]
            if len(keys) != len(set(keys)):
                raise ValueError(f"duplicate {label} source_key")
        return self


class FoundryCharacterSyncResult(ORMModel):
    character_id: UUID
    event_id: UUID | None
    trait_entries_added: int
    skill_entries_added: int
    passions_created: int
    passion_entries_added: int
    glory_adjustment: int
    stat_entries_added: int = 0
    inventory_items_created: int = 0
    inventory_entries_added: int = 0
    horses_created: int = 0
    horse_entries_added: int = 0
    ownership_changes: int = 0
    relatives_created: int = 0
    relative_details_updated: int = 0
    family_links_created: int = 0
    relationships_created: int = 0
    inheritance_records_created: int = 0
    history_entries_created: int = 0
    winter_records_created: int = 0
    wound_entries_added: int = 0
    changed: bool
