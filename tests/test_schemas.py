import pytest
from pydantic import ValidationError

from app.schemas import CampaignCreate, SessionCreate
from app.schemas.character import CharacterCreate, GloryCreate
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


def test_manor_requires_manor_location_kind() -> None:
    with pytest.raises(ValidationError):
        ManorCreate(location={"kind": "castle", "name": "Not a manor"})
