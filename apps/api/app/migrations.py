from __future__ import annotations

import asyncio
from pathlib import Path

import asyncpg

from .config import get_settings

MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "migrations"


def migration_dsn() -> str:
    return get_settings().database_url.replace(
        "postgresql+asyncpg://",
        "postgresql://",
        1,
    )


async def run_migrations() -> list[str]:
    connection = await asyncpg.connect(migration_dsn())
    executed: list[str] = []

    try:
        await connection.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version text PRIMARY KEY,
                applied_at timestamptz NOT NULL DEFAULT now()
            )
            """
        )

        rows = await connection.fetch(
            "SELECT version FROM schema_migrations ORDER BY version"
        )
        applied = {row["version"] for row in rows}

        for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
            version = path.stem
            if version in applied:
                continue

            sql = path.read_text(encoding="utf-8")
            async with connection.transaction():
                await connection.execute(sql)
                await connection.execute(
                    """
                    INSERT INTO schema_migrations (version)
                    VALUES ($1)
                    ON CONFLICT (version) DO NOTHING
                    """,
                    version,
                )

            executed.append(version)
            applied.add(version)
    finally:
        await connection.close()

    return executed


async def async_main() -> int:
    executed = await run_migrations()
    if executed:
        print("Applied migrations: " + ", ".join(executed))
    else:
        print("Database schema is up to date.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(async_main()))
