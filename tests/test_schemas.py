from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas import CampaignCreate, SessionCreate
from app.schemas.character import CharacterCreate, FoundryCharacterSnapshot, GloryCreate
from app.schemas.family import FamilyHistoryCreate, MarriageCreate
from app.schemas.location import ManorCreate


def test_campaign_slug_is_url_safe() -> None:
    campaign = CampaignCreate(name="Salisbury", slug="salisbury-485")
    assert campaign.current_year == 485


def test_campaign_rejects_bad_slug() -> None:
    with pytest.raises(ValidationError):
        CampaignCreate(name="Salisbury", slug="Salisbury Campaign")


def test_session_rejects_reversed_years() -> None:
    with pytest.raises(ValidationError):
        SessionCreate(
            session_number=1, title="The Beginning", in_game_start_year=486, in_game_end_year=485
        )


def test_player_knight_requires_player_name() -> None:
    with pytest.raises(ValidationError):
        CharacterCreate(kind="player_knight", name="Sir Sample")


def test_npc_does_not_require_player_name() -> None:
    npc = CharacterCreate(kind="npc", name="Roderick")
    assert npc.kind == "npc"


def test_glory_entry_must_change_total() -> None:
    with pytest.raises(ValidationError):
        GloryCreate(awarded_year=485, amount=0, reason="No change")


def test_foundry_snapshot_rejects_duplicate_item_source_keys() -> None:
    trait = {
        "source_key": "i.trait.merciful",
        "name": "Merciful",
        "opposed_name": "Vengeful",
        "value": 12,
        "opposed_value": 8,
    }
    with pytest.raises(ValidationError):
        FoundryCharacterSnapshot(
            effective_year=485,
            traits=[trait, trait],
            glory_total=100,
        )


def test_foundry_snapshot_accepts_statistics_inventory_and_horses() -> None:
    snapshot = FoundryCharacterSnapshot(
        effective_year=485,
        glory_total=1910,
        stats=[{"code": "siz", "value": 18}],
        inventory=[
            {
                "source_key": "Actor.test.Item.shield",
                "item_type": "armour",
                "name": "Shield",
                "equipped": True,
                "armour_points": 6,
            }
        ],
        horses=[
            {
                "source_key": "Actor.test.Item.horse",
                "name": "Bucephalus",
                "breed": "Courser",
                "siz": 30,
            }
        ],
    )
    assert snapshot.stats[0].code == "siz"
    assert snapshot.inventory[0].armour_points == 6
    assert snapshot.horses[0].breed == "Courser"


def test_manor_requires_manor_location_kind() -> None:
    with pytest.raises(ValidationError):
        ManorCreate(location={"kind": "castle", "name": "Not a manor"})


def test_ancestral_history_supports_pre_480_entries() -> None:
    entry = FamilyHistoryCreate(
        start_year=439, title="Ancestral service", summary="User-entered history"
    )
    assert entry.start_year == 439


def test_glory_history_requires_an_ancestor() -> None:
    with pytest.raises(ValidationError):
        FamilyHistoryCreate(
            start_year=439, title="Ancestral service", summary="History", glory_amount=100
        )


def test_marriage_requires_distinct_spouses() -> None:
    character_id = uuid4()
    with pytest.raises(ValidationError):
        MarriageCreate(spouse_one_id=character_id, spouse_two_id=character_id, start_year=480)
