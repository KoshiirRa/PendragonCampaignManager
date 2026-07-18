from app.models import CharacterPassion, SkillDefinition, TraitDefinition


def test_foundry_created_records_use_database_timestamps() -> None:
    for model in (TraitDefinition, SkillDefinition, CharacterPassion):
        assert model.__table__.c.created_at.server_default is not None
