import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr, ValidationError

from app.config import Settings
from app.main import app, health
from app.security import api_keys_match


@pytest.mark.asyncio
async def test_health_is_public() -> None:
    assert await health() == {"status": "ok"}


def test_api_key_comparison() -> None:
    expected = SecretStr("test-secret")
    assert api_keys_match(expected, "test-secret")
    assert not api_keys_match(expected, "wrong-secret")
    assert not api_keys_match(expected, None)


def test_development_can_disable_api_key() -> None:
    assert api_keys_match(None, None)


def test_production_requires_api_key() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, app_env="production", api_key=None)


def test_production_rejects_local_database() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, app_env="production", api_key="x" * 32)


def test_privacy_policy_is_public_and_complete() -> None:
    response = TestClient(app).get("/privacy")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "Pendragon Campaign Manager Privacy Policy" in response.text
    assert "Information processed" in response.text
    assert "Retention" in response.text
    assert "GitHub issue tracker" in response.text
