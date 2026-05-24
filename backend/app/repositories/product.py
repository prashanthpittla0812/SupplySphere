from typing import Optional, List, Tuple, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.repositories.base import BaseRepository
from app.models.product import Product
from app.models.inventory import Inventory


class ProductRepository(BaseRepository[Product]):
    def __init__(self, session: AsyncSession):
        super().__init__(Product, session)

    async def get_by_sku(self, sku: str) -> Optional[Product]:
        query = select(Product).where(Product.sku == sku, Product.is_deleted == False)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_vendor(self, vendor_id: UUID) -> List[Product]:
        query = select(Product).where(Product.vendor_id == vendor_id, Product.is_deleted == False)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_category(self, category: str, skip: int = 0, limit: int = 20) -> Tuple[List[Product], int]:
        q = select(Product).where(Product.category == category, Product.is_deleted == False).offset(skip).limit(limit).order_by(Product.created_at.desc())
        count_q = select(func.count(Product.id)).where(Product.category == category, Product.is_deleted == False)
        result = await self.session.execute(q)
        items = list(result.scalars().all())
        total_result = await self.session.execute(count_q)
        total = total_result.scalar() or 0
        return items, total

    async def search(
        self, query: str, skip: int = 0, limit: int = 20
    ) -> Tuple[List[Product], int]:
        search_filter = or_(
            Product.name.ilike(f"%{query}%"),
            Product.sku.ilike(f"%{query}%"),
            Product.category.ilike(f"%{query}%"),
            Product.description.ilike(f"%{query}%"),
        )
        q = select(Product).where(search_filter, Product.is_deleted == False).offset(skip).limit(limit).order_by(Product.created_at.desc())
        count_q = select(func.count(Product.id)).where(search_filter, Product.is_deleted == False)
        result = await self.session.execute(q)
        items = list(result.scalars().all())
        total_result = await self.session.execute(count_q)
        total = total_result.scalar() or 0
        return items, total

    async def get_low_stock_products(self) -> List[Product]:
        subq = (
            select(Inventory.product_id, func.coalesce(func.sum(Inventory.quantity), 0).label("total_qty"))
            .where(Inventory.is_deleted == False)
            .group_by(Inventory.product_id)
            .subquery()
        )
        query = (
            select(Product)
            .join(subq, Product.id == subq.c.product_id)
            .where(Product.is_deleted == False, subq.c.total_qty < Product.min_stock_level)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_category_breakdown(self) -> List[Dict[str, Any]]:
        query = select(
            Product.category,
            func.count(Product.id).label("count"),
            func.sum(Product.unit_price * func.coalesce(
                select(func.sum(Inventory.quantity))
                .where(Inventory.product_id == Product.id, Inventory.is_deleted == False)
                .scalar_subquery(), 0
            )).label("total_value"),
        ).where(Product.is_deleted == False).group_by(Product.category)
        result = await self.session.execute(query)
        rows = result.all()
        return [
            {"category": row.category, "count": row.count, "total_value": float(row.total_value or 0)}
            for row in rows
        ]
