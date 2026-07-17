import pytest
from pydantic import ValidationError

from app.schemas import CampaignCreate, SessionCreate


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
