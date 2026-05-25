"""Neon PostgreSQL Connection Test

Usage:
    python test_connection.py

Tests:
    - Async engine creation with pooling
    - Database connectivity
    - Basic query execution (SELECT 1)
    - Table reflection (lists all tables)
    - Connection pool stats
"""

import asyncio
import sys
import time

from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.database import (
    async_engine,
    sync_engine,
    ASYNC_DATABASE_URL,
    SYNC_DATABASE_URL,
    IS_SQLITE,
    POOL_SIZE,
    MAX_OVERFLOW,
)


async def test_async_connection():
    print("=" * 60)
    print("SUPPLYSPHERE - DATABASE CONNECTION TEST")
    print("=" * 60)
    print(f"Project:     {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"DB Type:     {'SQLite' if IS_SQLITE else 'PostgreSQL'}")
    print(f"Async URL:   {ASYNC_DATABASE_URL}")
    print(f"Sync URL:    {SYNC_DATABASE_URL}")
    print(f"Pool Size:   {POOL_SIZE}")
    print(f"Overflow:    {MAX_OVERFLOW}")
    print(f"Pool PrePing:{'Yes' if not IS_SQLITE else 'N/A (SQLite)'}")
    print(f"Pool Recycle:{'3600s' if not IS_SQLITE else 'N/A (SQLite)'}")
    print("-" * 60)

    try:
        start = time.time()
        async with async_engine.connect() as conn:
            result = await conn.execute(text("SELECT 1 AS test"))
            row = result.fetchone()
            elapsed = time.time() - start
            print(f"[PASS] Async connection established in {elapsed:.3f}s")
            print(f"[PASS] Basic query result: SELECT 1 = {row[0]}")

        async with async_engine.connect() as conn:
            result = await conn.execute(
                text(
                    "SELECT current_database(), current_schema(), version()"
                    if not IS_SQLITE
                    else "SELECT 'supplysphere', 'main', sqlite_version()"
                )
            )
            row = result.fetchone()
            print(f"[INFO] Database: {row[0]}")
            print(f"[INFO] Schema:   {row[1]}")
            print(f"[INFO] Version:  {row[2]}")

        async with async_engine.connect() as conn:
            result = await conn.execute(
                text(
                    "SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname='public' ORDER BY tablename"
                    if not IS_SQLITE
                    else "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
                )
            )
            tables = result.fetchall()
            print(f"\n[TABLES] Found {len(tables)} table(s):")
            for t in tables:
                print(f"  - {t[0]}")

        pool_state = async_engine.pool.status()
        print(f"\n[POOL] Size: {async_engine.pool.size()}")
        print(f"[POOL] Checked-in: {async_engine.pool.checkedin()}")
        print(f"[POOL] Overflow: {async_engine.pool.overflow()}")

        print("-" * 60)
        print("[PASS] All async connection tests passed!")
        return True

    except SQLAlchemyError as e:
        print(f"[FAIL] Database error: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}", file=sys.stderr)
        return False


async def main():
    success = await test_async_connection()
    await async_engine.dispose()
    sync_engine.dispose()
    print("=" * 60)
    if success:
        print("STATUS: DATABASE CONNECTION OK")
    else:
        print("STATUS: DATABASE CONNECTION FAILED", file=sys.stderr)
    print("=" * 60)
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
