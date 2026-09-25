from app.config import Settings


def test_test_fixtures_are_hidden_by_default() -> None:
    settings = Settings(_env_file=None)
    assert settings.allow_test_fixtures is False
