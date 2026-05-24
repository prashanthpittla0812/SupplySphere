from typing import Optional, List, Tuple, Dict, Any
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import selectinload

from app.repositories.base import BaseRepository
from app.models.inventory import Inventory


class InventoryRepository(BaseRepository[Inventory]):
    def __init__(self, session: AsyncSession):
        super().__init__(Inventory, session)

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 20,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
        filters: Optional[Dict[str, Any]] = None,
        search: Optional[str] = None,
        search_fields: Optional[List[str]] = None,
    ) -> tuple[List[Inventory], int]:
        query = (
            select(Inventory)
            .options(selectinload(Inventory.product), selectinload(Inventory.warehouse))
            .where(Inventory.is_deleted == False)
        )
        count_query = select(func.count(Inventory.id)).where(Inventory.is_deleted == False)

        if filters:
            for key, value in filters.items():
                if hasattr(Inventory, key) and value is not None:
                    query = query.where(getattr(Inventory, key) == value)
                    count_query = count_query.where(getattr(Inventory, key) == value)

        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0

        if sort_by and hasattr(Inventory, sort_by):
            sort_col = getattr(Inventory, sort_by)
            query = query.order_by(sort_col.desc() if sort_order == "desc" else sort_col.asc())
        else:
            query = query.order_by(Inventory.created_at.desc())

        result = await self.session.execute(query.offset(skip).limit(limit))
        return list(result.scalars().all()), total

    async def get_by_product_and_warehouse(
        self, product_id: UUID, warehouse_id: UUID
    ) -> Optional[Inventory]:
        query = (
            select(Inventory)
            .options(selectinload(Inventory.product), selectinload(Inventory.warehouse))
            .where(
                Inventory.product_id == product_id,
                Inventory.warehouse_id == warehouse_id,
                Inventory.is_deleted == False,
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_product(self, product_id: UUID) -> List[Inventory]:
        query = (
            select(Inventory)
            .options(selectinload(Inventory.product), selectinload(Inventory.warehouse))
            .where(Inventory.product_id == product_id, Inventory.is_deleted == False)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_warehouse(self, warehouse_id: UUID) -> List[Inventory]:
        query = (
            select(Inventory)
            .options(selectinload(Inventory.product), selectinload(Inventory.warehouse))
            .where(Inventory.warehouse_id == warehouse_id, Inventory.is_deleted == False)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_low_stock_items(self, min_stock_map: Dict[UUID, float]) -> List[Inventory]:
        conditions = []
        for product_id, min_qty in min_stock_map.items():
            conditions.append(
                and_(Inventory.product_id == product_id, Inventory.quantity < min_qty)
            )
        if not conditions:
            return []
        query = select(Inventory).where(
            or_(*conditions), Inventory.is_deleted == False
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def adjust_quantity(
        self, inventory_id: UUID, adjustment_type: str, quantity: float, reason: str
    ) -> Optional[Inventory]:
        inv = await self.get_by_id(inventory_id)
        if not inv:
            return None
        if adjustment_type == "add":
            inv.quantity += quantity
        elif adjustment_type == "subtract":
            inv.quantity -= quantity
        elif adjustment_type == "set":
            inv.quantity = quantity
        inv.last_count_date = datetime.now(timezone.utc)
        await self.session.flush()
        await self.session.refresh(inv)
        return inv

    async def reserve_quantity(self, inventory_id: UUID, quantity: float) -> Optional[Inventory]:
        inv = await self.get_by_id(inventory_id)
        if not inv:
            return None
        if inv.quantity - inv.reserved_quantity < quantity:
            raise ValueError("Insufficient available quantity")
        inv.reserved_quantity += quantity
        await self.session.flush()
        await self.session.refresh(inv)
        return inv

    async def release_reserved(self, inventory_id: UUID, quantity: float) -> Optional[Inventory]:
        inv = await self.get_by_id(inventory_id)
        if not inv:
            return None
        inv.reserved_quantity -= quantity
        if inv.reserved_quantity < 0:
            inv.reserved_quantity = 0
        await self.session.flush()
        await self.session.refresh(inv)
        return inv

    async def get_warehouse_inventory_summary(self, warehouse_id: UUID) -> Dict[str, Any]:
        query = select(
            func.count(Inventory.id).label("total_items"),
            func.sum(Inventory.quantity).label("total_quantity"),
            func.sum(Inventory.reserved_quantity).label("total_reserved"),
            func.sum(Inventory.quantity - Inventory.reserved_quantity).label("available_quantity"),
        ).where(Inventory.warehouse_id == warehouse_id, Inventory.is_deleted == False)
        result = await self.session.execute(query)
        row = result.one()
        return {
            "total_items": row.total_items or 0,
            "total_quantity": float(row.total_quantity or 0),
            "total_reserved": float(row.total_reserved or 0),
            "available_quantity": float(row.available_quantity or 0),
        }
