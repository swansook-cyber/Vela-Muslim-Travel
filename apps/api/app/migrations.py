from __future__ import annotations

import asyncio
from pathlib import Path

from sqlalchemy import text

from .db import SessionLocal

MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "migrations"


async def ensure_migration_table() -> None:
    async with SessionLocal() as session, session.begin():
        await session.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version text PRIMARY KEY,
                    applied_at timestamptz NOT NULL DEFAULT now()
                )
                """
            )
        )


async def applied_versions() -> set[str]:
    async with SessionLocal() as session:
        rows = (
            await session.execute(
                text("SELECT version FROM schema_migrations ORDER BY version")
            )
        ).scalars().all()
    return set(rows)


async def apply_migration(path: Path) -> None:
    sql = path.read_text(encoding="utf-8")
    version = path.stem

    async with SessionLocal() as session, session.begin():
        await session.execute(text(sql))
        await session.execute(
            text(
                """
                INSERT INTO schema_migrations (version)
                VALUES (:version)
                ON CONFLICT (version) DO NOTHING
                """
            ),
            {"version": version},
        )


async def run_migrations() -> list[str]:
    await ensure_migration_table()
    applied = await applied_versions()
    executed: list[str] = []

    for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
        version = path.stem
        if version in applied:
            continue
        await apply_migration(path)
        executed.append(version)

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
