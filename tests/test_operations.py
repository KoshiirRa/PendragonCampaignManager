import pytest
from pydantic import SecretStr, ValidationError

from app.config import Settings
from app.main import health
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
