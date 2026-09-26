from pathlib import Path

import yaml


def test_production_compose_passes_runtime_controls_to_api() -> None:
    compose_path = Path(__file__).resolve().parents[3] / "docker-compose.prod.yml"
    compose = yaml.safe_load(compose_path.read_text(encoding="utf-8"))

    environment = compose["services"]["api"]["environment"]

    required = {
        "ROUTE_REQUEST_TIMEOUT_SECONDS",
        "ROUTING_CACHE_TTL_SECONDS",
        "ROUTING_CACHE_MAX_ENTRIES",
        "ROUTING_MIN_INTERVAL_SECONDS",
        "ROUTING_USER_AGENT",
        "GEOCODING_CACHE_TTL_SECONDS",
        "GEOCODING_CACHE_MAX_ENTRIES",
        "GEOCODING_MIN_INTERVAL_SECONDS",
    }

    assert required.issubset(environment)
