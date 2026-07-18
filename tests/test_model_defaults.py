from sqlalchemy import Enum

from app.models import CharacterPassion, Event, SkillDefinition, TraitDefinition


def test_foundry_created_records_use_database_timestamps() -> None:
    for model in (TraitDefinition, SkillDefinition, CharacterPassion):
        assert model.__table__.c.created_at.server_default is not None


def test_event_visibility_uses_the_postgresql_enum() -> None:
    column_type = Event.__table__.c.visibility.type
    assert isinstance(column_type, Enum)
    assert column_type.name == "event_visibility"
