from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.repositories.base import BaseRepository
from app.models.warehouse import Warehouse


class WarehouseRepository(BaseRepository[Warehouse]):
    def __init__(self, session: AsyncSession):
        super().__init__(Warehouse, session)

    async def get_by_code(self, code: str) -> Optional[Warehouse]:
        query = select(Warehouse).where(Warehouse.code == code, Warehouse.is_deleted == False)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_available_warehouses(self) -> List[Warehouse]:
        query = select(Warehouse).where(
            Warehouse.is_active == True, Warehouse.is_deleted == False
        ).order_by(Warehouse.name)
        result = await self.session.execute(query)
        return list(result.scalars().all())
