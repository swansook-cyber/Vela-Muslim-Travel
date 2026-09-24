from app.config import Settings


def test_cors_origins_are_trimmed() -> None:
    settings = Settings(cors_origins="http://a.test, http://b.test ,,")
    assert settings.cors_origin_list == ["http://a.test", "http://b.test"]
