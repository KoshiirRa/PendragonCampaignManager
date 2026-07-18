from decimal import Decimal
from uuid import UUID

from app.schemas.common import ORMModel


class PlayerEvent(ORMModel):
    id: UUID
    year: int
    date: str | None
    event_type: str
    title: str
    description: str | None


class PlayerPerson(ORMModel):
    id: UUID
    name: str
    player_name: str
    description: str | None
    glory: int


class PlayerFamilyMember(ORMModel):
    id: UUID
    name: str
    membership_type: str
    start_year: int | None
    end_year: int | None


class PlayerFamily(ORMModel):
    id: UUID
    name: str
    founding_year: int | None
    culture: str | None
    coat_of_arms: str | None
    motto: str | None
    notes: str | None
    origin_location: str | None
    members: list[PlayerFamilyMember]


class PlayerManorItem(ORMModel):
    id: UUID
    name: str
    description: str | None
    status: str | None = None


class PlayerManorDefense(ORMModel):
    id: UUID
    name: str
    defensive_value: int


class PlayerManor(ORMModel):
    id: UUID
    name: str
    description: str | None
    holder: str | None
    customary_income: Decimal | None
    population: int | None
    base_defensive_value: int
    improvements: list[PlayerManorItem]
    special_features: list[PlayerManorItem]
    defenses: list[PlayerManorDefense]


class PlayerChronicleSection(ORMModel):
    character_id: UUID
    heading: str
    body: str


class PlayerChronicle(ORMModel):
    id: UUID
    year: int
    revision: int
    title: str
    opening: str
    closing: str
    sections: list[PlayerChronicleSection]


class CampaignPlayerView(ORMModel):
    campaign_id: UUID
    campaign_name: str
    current_year: int
    events: list[PlayerEvent]
    people: list[PlayerPerson]
    families: list[PlayerFamily]
    manors: list[PlayerManor]
    chronicles: list[PlayerChronicle]
