"""SupplySphere seeding utilities."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


class SeedLogger:
    def __init__(self, silent: bool = False):
        self.silent = silent

    def info(self, msg: str):
        if not self.silent:
            print(f"  [INFO] {msg}")

    def ok(self, msg: str):
        if not self.silent:
            print(f"  [OK]   {msg}")

    def skip(self, msg: str):
        if not self.silent:
            print(f"  [SKIP] {msg}")


async def _table_is_empty(db: AsyncSession, model) -> bool:
    result = await db.execute(select(func.count(model.id)))
    return (result.scalar() or 0) == 0
