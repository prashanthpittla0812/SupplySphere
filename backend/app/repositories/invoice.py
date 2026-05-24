from typing import Optional, List, Tuple, Dict, Any
from uuid import UUID
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, extract, cast, Date

from app.repositories.base import BaseRepository
from app.models.invoice import Invoice


class InvoiceRepository(BaseRepository[Invoice]):
    def __init__(self, session: AsyncSession):
        super().__init__(Invoice, session)

    async def get_by_invoice_number(self, invoice_number: str) -> Optional[Invoice]:
        query = select(Invoice).where(
            Invoice.invoice_number == invoice_number, Invoice.is_deleted == False
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_order(self, order_id: UUID) -> List[Invoice]:
        query = select(Invoice).where(
            Invoice.order_id == order_id, Invoice.is_deleted == False
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_vendor(
        self, vendor_id: UUID, skip: int = 0, limit: int = 20
    ) -> Tuple[List[Invoice], int]:
        q = select(Invoice).where(
            Invoice.vendor_id == vendor_id, Invoice.is_deleted == False
        ).offset(skip).limit(limit).order_by(Invoice.created_at.desc())
        count_q = select(func.count(Invoice.id)).where(
            Invoice.vendor_id == vendor_id, Invoice.is_deleted == False
        )
        result = await self.session.execute(q)
        items = list(result.scalars().all())
        total_result = await self.session.execute(count_q)
        total = total_result.scalar() or 0
        return items, total

    async def get_by_status(
        self, status: str, skip: int = 0, limit: int = 20
    ) -> Tuple[List[Invoice], int]:
        q = select(Invoice).where(
            Invoice.status == status, Invoice.is_deleted == False
        ).offset(skip).limit(limit).order_by(Invoice.created_at.desc())
        count_q = select(func.count(Invoice.id)).where(
            Invoice.status == status, Invoice.is_deleted == False
        )
        result = await self.session.execute(q)
        items = list(result.scalars().all())
        total_result = await self.session.execute(count_q)
        total = total_result.scalar() or 0
        return items, total

    async def get_overdue_invoices(self) -> List[Invoice]:
        now = datetime.now(timezone.utc)
        query = select(Invoice).where(
            Invoice.due_date < now,
            Invoice.status.in_(["pending", "sent"]),
            Invoice.is_deleted == False,
        ).order_by(Invoice.due_date.asc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_revenue_data(self, days: int = 30) -> List[Dict[str, Any]]:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        query = select(
            cast(Invoice.created_at, Date).label("date"),
            func.sum(Invoice.total_amount).label("revenue"),
            func.count(Invoice.id).label("orders"),
        ).where(
            Invoice.is_deleted == False,
            Invoice.status == "paid",
            Invoice.created_at >= since,
        ).group_by(cast(Invoice.created_at, Date)).order_by(cast(Invoice.created_at, Date))
        result = await self.session.execute(query)
        rows = result.all()
        return [
            {"date": str(row.date), "revenue": float(row.revenue or 0), "orders": row.orders}
            for row in rows
        ]

    async def generate_invoice_number(self) -> str:
        year = datetime.now(timezone.utc).year
        count_q = select(func.count(Invoice.id)).where(Invoice.is_deleted == False)
        result = await self.session.execute(count_q)
        count = result.scalar() or 0
        return f"INV-{year}-{count + 1:05d}"

    async def get_total_revenue(self, filters: Optional[Dict[str, Any]] = None) -> float:
        query = select(func.sum(Invoice.total_amount)).where(
            Invoice.is_deleted == False, Invoice.status == "paid"
        )
        if filters:
            for key, value in filters.items():
                if hasattr(Invoice, key) and value is not None:
                    query = query.where(getattr(Invoice, key) == value)
        result = await self.session.execute(query)
        return float(result.scalar() or 0)
