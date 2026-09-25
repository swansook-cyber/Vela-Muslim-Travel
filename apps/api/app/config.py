from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = (
        "postgresql+asyncpg://vela:vela_dev@localhost:5432/vela_muslim_travel"
    )
    routing_provider: str = "osrm"
    osrm_base_url: str = "https://router.project-osrm.org"
    route_request_timeout_seconds: float = 15.0
    routing_cache_ttl_seconds: int = 300
    routing_cache_max_entries: int = 256
    routing_min_interval_seconds: float = 0.25
    routing_user_agent: str = (
        "VelaMuslimTravel/0.1 (+https://github.com/swansook-cyber/Vela-Muslim-Travel)"
    )
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    admin_api_key: str | None = None
    geocoding_provider: str = "nominatim"
    nominatim_base_url: str = "https://nominatim.openstreetmap.org"
    geocoding_user_agent: str = (
        "VelaMuslimTravel/0.1 (+https://github.com/swansook-cyber/Vela-Muslim-Travel)"
    )
    geocoding_cache_ttl_seconds: int = 86400
    geocoding_cache_max_entries: int = 256
    geocoding_min_interval_seconds: float = 1.1

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
