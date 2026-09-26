from __future__ import annotations

import argparse
from pathlib import Path


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def validate(values: dict[str, str]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    postgres_password = values.get("POSTGRES_PASSWORD", "")
    if len(postgres_password) < 20 or "change-me" in postgres_password.lower():
        errors.append("POSTGRES_PASSWORD must be a non-default value of at least 20 characters")

    admin_key = values.get("ADMIN_API_KEY", "")
    if len(admin_key) < 24 or "change-me" in admin_key.lower():
        errors.append("ADMIN_API_KEY must be a non-default value of at least 24 characters")

    cors_origins = [
        item.strip()
        for item in values.get("CORS_ORIGINS", "").split(",")
        if item.strip()
    ]
    if not cors_origins:
        errors.append("CORS_ORIGINS must contain the production HTTPS origin")
    elif any(not origin.startswith("https://") for origin in cors_origins):
        errors.append("Every production CORS_ORIGINS entry must use https://")

    if values.get("ALLOW_TEST_FIXTURES", "false").lower() != "false":
        errors.append("ALLOW_TEST_FIXTURES must be false in production")

    if not values.get("GOOGLE_PLACES_API_KEY"):
        warnings.append(
            "GOOGLE_PLACES_API_KEY is blank; Admin Google coordinate resolver will be disabled"
        )

    osrm = values.get("OSRM_BASE_URL", "")
    if "router.project-osrm.org" in osrm:
        warnings.append(
            "Public OSRM is configured; acceptable for pilot use but not a production SLA"
        )

    nominatim = values.get("NOMINATIM_BASE_URL", "")
    if "nominatim.openstreetmap.org" in nominatim:
        warnings.append(
            "Public Nominatim is configured; keep request throttling enabled and do not assume an SLA"
        )

    return errors, warnings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate Vela Muslim Travel production environment before deploy."
    )
    parser.add_argument(
        "env_file",
        nargs="?",
        default="deploy/.env",
        type=Path,
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not args.env_file.exists():
        print(f"ERROR: environment file not found: {args.env_file}")
        return 2

    values = load_env(args.env_file)
    errors, warnings = validate(values)

    for warning in warnings:
        print(f"WARNING: {warning}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 2

    print("Production preflight passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
