from typing import Optional, List, Tuple, Dict, Any
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_, extract

from app.repositories.base import BaseRepository
from app.models.order import PurchaseOrder, PurchaseOrderItem


class OrderRepository(BaseRepository[PurchaseOrder]):
    def __init__(self, session: AsyncSession):
        super().__init__(PurchaseOrder, session)

    async def get_by_order_number(self, order_number: str) -> Optional[PurchaseOrder]:
        query = select(PurchaseOrder).where(
            PurchaseOrder.order_number == order_number, PurchaseOrder.is_deleted == False
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_vendor(
        self, vendor_id: UUID, skip: int = 0, limit: int = 20
    ) -> Tuple[List[PurchaseOrder], int]:
        q = select(PurchaseOrder).where(
            PurchaseOrder.vendor_id == vendor_id, PurchaseOrder.is_deleted == False
        ).offset(skip).limit(limit).order_by(PurchaseOrder.created_at.desc())
        count_q = select(func.count(PurchaseOrder.id)).where(
            PurchaseOrder.vendor_id == vendor_id, PurchaseOrder.is_deleted == False
        )
        result = await self.session.execute(q)
        items = list(result.scalars().all())
        total_result = await self.session.execute(count_q)
        total = total_result.scalar() or 0
        return items, total

    async def get_by_status(
        self, status: str, skip: int = 0, limit: int = 20
    ) -> Tuple[List[PurchaseOrder], int]:
        q = select(PurchaseOrder).where(
            PurchaseOrder.status == status, PurchaseOrder.is_deleted == False
        ).offset(skip).limit(limit).order_by(PurchaseOrder.created_at.desc())
        count_q = select(func.count(PurchaseOrder.id)).where(
            PurchaseOrder.status == status, PurchaseOrder.is_deleted == False
        )
        result = await self.session.execute(q)
        items = list(result.scalars().all())
        total_result = await self.session.execute(count_q)
        total = total_result.scalar() or 0
        return items, total

    async def get_pending_approval(
        self, skip: int = 0, limit: int = 20
    ) -> Tuple[List[PurchaseOrder], int]:
        q = select(PurchaseOrder).where(
            PurchaseOrder.status == "pending_approval", PurchaseOrder.is_deleted == False
        ).offset(skip).limit(limit).order_by(PurchaseOrder.created_at.asc())
        count_q = select(func.count(PurchaseOrder.id)).where(
            PurchaseOrder.status == "pending_approval", PurchaseOrder.is_deleted == False
        )
        result = await self.session.execute(q)
        items = list(result.scalars().all())
        total_result = await self.session.execute(count_q)
        total = total_result.scalar() or 0
        return items, total

    async def get_recent_orders(self, limit: int = 10) -> List[PurchaseOrder]:
        query = select(PurchaseOrder).where(
            PurchaseOrder.is_deleted == False
        ).order_by(PurchaseOrder.created_at.desc()).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_order_status_distribution(self) -> List[Dict[str, Any]]:
        query = select(
            PurchaseOrder.status,
            func.count(PurchaseOrder.id).label("count"),
        ).where(PurchaseOrder.is_deleted == False).group_by(PurchaseOrder.status)
        result = await self.session.execute(query)
        rows = result.all()
        return [{"status": row.status, "count": row.count} for row in rows]

    async def get_monthly_trends(self, months: int = 12) -> List[Dict[str, Any]]:
        query = select(
            extract("year", PurchaseOrder.created_at).label("year"),
            extract("month", PurchaseOrder.created_at).label("month"),
            func.sum(PurchaseOrder.total_amount).label("revenue"),
            func.count(PurchaseOrder.id).label("orders"),
        ).where(
            PurchaseOrder.is_deleted == False,
            PurchaseOrder.status.in_(["approved", "completed", "delivered"]),
        ).group_by("year", "month").order_by("year", "month").limit(months)
        result = await self.session.execute(query)
        rows = result.all()
        return [
            {
                "year": int(row.year),
                "month": int(row.month),
                "revenue": float(row.revenue or 0),
                "orders": row.orders,
            }
            for row in rows
        ]

    async def generate_order_number(self) -> str:
        count = await self.get_order_count()
        year = datetime.now(timezone.utc).year
        return f"PO-{year}-{count + 1:05d}"

    async def get_order_count(self) -> int:
        query = select(func.count(PurchaseOrder.id)).where(PurchaseOrder.is_deleted == False)
        result = await self.session.execute(query)
        return result.scalar() or 0


class PurchaseOrderItemRepository(BaseRepository[PurchaseOrderItem]):
    def __init__(self, session: AsyncSession):
        super().__init__(PurchaseOrderItem, session)

    async def get_by_order(self, order_id: UUID) -> List[PurchaseOrderItem]:
        query = select(PurchaseOrderItem).where(
            PurchaseOrderItem.order_id == order_id, PurchaseOrderItem.is_deleted == False
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_item_status(
        self, item_id: UUID, status: str, received_quantity: Optional[float] = None
    ) -> Optional[PurchaseOrderItem]:
        item = await self.get_by_id(item_id)
        if not item:
            return None
        item.status = status
        if received_quantity is not None:
            item.received_quantity = received_quantity
        await self.session.flush()
        await self.session.refresh(item)
        return item
