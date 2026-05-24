from datetime import datetime, timedelta, timezone
from typing import Optional, List, Tuple, Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.invoice import Invoice
from app.models.order import PurchaseOrder
from app.schemas.common import PaginationMeta
from app.core.exceptions import NotFoundException, BadRequestException
from app.services.audit_log import AuditLogService


class InvoiceRepository:
    def __init__(self, session: AsyncSession):
        from app.repositories.base import BaseRepository
        self._repo = BaseRepository(Invoice, session)
        self.session = session

    async def get_by_id(self, id: UUID) -> Optional[Invoice]:
        id = id if isinstance(id, UUID) else UUID(str(id))
        return await self._repo.get_by_id(id)

    async def create(self, **kwargs) -> Invoice:
        return await self._repo.create(**kwargs)

    async def update(self, id: UUID, **kwargs) -> Optional[Invoice]:
        id = id if isinstance(id, UUID) else UUID(str(id))
        return await self._repo.update(id, **kwargs)

    async def soft_delete(self, id: UUID) -> bool:
        id = id if isinstance(id, UUID) else UUID(str(id))
        return await self._repo.soft_delete(id)

    async def list_all(self, **kwargs) -> Tuple[List[Invoice], int]:
        filters = kwargs.get("filters")
        if filters:
            for key in ("order_id", "vendor_id"):
                if key in filters and filters[key] is not None and not isinstance(filters[key], UUID):
                    filters[key] = UUID(str(filters[key]))
        return await self._repo.list_all(**kwargs)

    async def get_overdue(self) -> List[Invoice]:
        query = select(Invoice).where(
            Invoice.is_deleted == False,
            Invoice.status == "sent",
            Invoice.due_date < datetime.now(timezone.utc),
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_revenue_data(self, days: int = 30) -> List[Dict[str, Any]]:
        from sqlalchemy import extract
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        query = select(
            func.date(Invoice.paid_date).label("date"),
            func.coalesce(func.sum(Invoice.amount_paid), 0).label("revenue"),
        ).where(
            Invoice.is_deleted == False,
            Invoice.status == "paid",
            Invoice.paid_date >= cutoff,
        ).group_by(func.date(Invoice.paid_date)).order_by(func.date(Invoice.paid_date))
        result = await self.session.execute(query)
        rows = result.all()
        return [{"date": str(row.date), "revenue": float(row.revenue)} for row in rows]

    async def get_total_revenue(self, filters: Optional[Dict[str, Any]] = None) -> float:
        query = select(func.coalesce(func.sum(Invoice.amount_paid), 0)).where(
            Invoice.is_deleted == False,
            Invoice.status == "paid",
        )
        if filters:
            for key, value in filters.items():
                if hasattr(Invoice, key) and value is not None:
                    query = query.where(getattr(Invoice, key) == value)
        result = await self.session.execute(query)
        return float(result.scalar() or 0)


class InvoiceService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.invoice_repo = InvoiceRepository(db)
        self.audit_log_service = AuditLogService(db)

    def _uuid(self, value) -> UUID:
        return value if isinstance(value, UUID) else UUID(str(value))

    async def create_invoice(self, data, user_id: UUID) -> Invoice:
        order_query = select(PurchaseOrder).where(PurchaseOrder.id == data.order_id, PurchaseOrder.is_deleted == False)
        order_result = await self.db.execute(order_query)
        order = order_result.scalar_one_or_none()
        if not order:
            raise NotFoundException("Order not found")

        invoice_number = await self._generate_invoice_number()

        subtotal = getattr(data, "subtotal", None) or order.subtotal or order.total_amount
        tax_amount = getattr(data, "tax_amount", None)
        if tax_amount is None:
            tax_amount = order.tax_amount or 0.0
        total_amount = getattr(data, "total_amount", None) or (subtotal + tax_amount)
        balance_due = total_amount - getattr(data, 'amount_paid', 0.0)

        invoice = await self.invoice_repo.create(
            invoice_number=invoice_number,
            order_id=data.order_id,
            vendor_id=getattr(data, 'vendor_id', order.vendor_id),
            order_number=getattr(order, "order_number", None),
            issue_date=getattr(data, "issue_date", None),
            subtotal=subtotal,
            tax_amount=tax_amount,
            total_amount=total_amount,
            amount_paid=getattr(data, 'amount_paid', 0.0),
            balance_due=balance_due,
            status="draft",
            due_date=getattr(data, 'due_date', None),
            notes=getattr(data, 'notes', None),
            created_by=user_id,
        )
        return invoice

    async def create(self, data, current_user=None) -> Invoice:
        user_id = getattr(current_user, "id", current_user)
        return await self.create_invoice(data, user_id)

    async def update_invoice(self, invoice_id: UUID, data) -> Invoice:
        invoice_id = self._uuid(invoice_id)
        invoice = await self.invoice_repo.get_by_id(invoice_id)
        if not invoice:
            raise NotFoundException("Invoice not found")

        update_data = data.model_dump(exclude_unset=True)
        invoice = await self.invoice_repo.update(invoice_id, **update_data)
        return invoice

    async def update(self, invoice_id: UUID, data) -> Invoice:
        return await self.update_invoice(invoice_id, data)

    async def delete_invoice(self, invoice_id: UUID) -> bool:
        invoice_id = self._uuid(invoice_id)
        invoice = await self.invoice_repo.get_by_id(invoice_id)
        if not invoice:
            raise NotFoundException("Invoice not found")
        return await self.invoice_repo.soft_delete(invoice_id)

    async def delete(self, invoice_id: UUID) -> bool:
        return await self.delete_invoice(invoice_id)

    async def get_invoice(self, invoice_id: UUID) -> Invoice:
        invoice_id = self._uuid(invoice_id)
        invoice = await self.invoice_repo.get_by_id(invoice_id)
        if not invoice:
            raise NotFoundException("Invoice not found")
        return invoice

    async def get_by_id(self, invoice_id: UUID) -> Invoice:
        return await self.get_invoice(invoice_id)

    async def list(self, params, skip: int = 0, search: Optional[str] = None, **filters) -> Tuple[List[Invoice], int]:
        filters = {key: value for key, value in filters.items() if value is not None}
        for key in ("order_id", "vendor_id"):
            if key in filters:
                filters[key] = self._uuid(filters[key])
        return await self.invoice_repo.list_all(
            skip=skip,
            limit=params.per_page,
            sort_by=params.sort_by,
            sort_order=params.sort_order,
            filters=filters or None,
            search=search,
            search_fields=["invoice_number"],
        )

    async def list_invoices(
        self,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        status: Optional[str] = None,
        vendor_id: Optional[UUID] = None,
        order_id: Optional[UUID] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Tuple[List[Invoice], PaginationMeta]:
        filters = {}
        if status:
            filters["status"] = status
        if vendor_id:
            filters["vendor_id"] = vendor_id
        if order_id:
            filters["order_id"] = order_id

        skip = (page - 1) * per_page
        items, total = await self.invoice_repo.list_all(
            skip=skip,
            limit=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            filters=filters,
            search=search,
            search_fields=["invoice_number"],
        )
        total_pages = max(1, (total + per_page - 1) // per_page)
        meta = PaginationMeta(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )
        return items, meta

    async def record_payment(self, invoice_id: UUID, data, current_user=None) -> Invoice:
        invoice_id = self._uuid(invoice_id)
        invoice = await self.invoice_repo.get_by_id(invoice_id)
        if not invoice:
            raise NotFoundException("Invoice not found")

        payment_amount = data.amount if hasattr(data, "amount") else data.get("amount", 0)
        new_amount_paid = invoice.amount_paid + payment_amount
        new_balance_due = invoice.total_amount - new_amount_paid

        update_kwargs = {
            "amount_paid": new_amount_paid,
            "balance_due": max(new_balance_due, 0.0),
        }

        if new_balance_due <= 0:
            update_kwargs["status"] = "paid"
            update_kwargs["paid_date"] = datetime.now(timezone.utc)

        invoice = await self.invoice_repo.update(invoice_id, **update_kwargs)
        return invoice

    async def get_overdue_invoices(self) -> List[Invoice]:
        return await self.invoice_repo.get_overdue()

    async def get_overdue(self, skip: int = 0, per_page: int = 20) -> Tuple[List[Invoice], int]:
        items = await self.get_overdue_invoices()
        return items[skip : skip + per_page], len(items)

    async def get_revenue_data(self, days: int = 30, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        return await self.invoice_repo.get_revenue_data(days)

    async def get_total_revenue(self, filters: Optional[Dict[str, Any]] = None) -> float:
        return await self.invoice_repo.get_total_revenue(filters)

    async def generate_invoice_pdf(self, invoice_id: UUID) -> str:
        invoice_id = self._uuid(invoice_id)
        invoice = await self.invoice_repo.get_by_id(invoice_id)
        if not invoice:
            raise NotFoundException("Invoice not found")
        pdf_url = f"/invoices/{invoice_id}/pdf"
        return pdf_url

    async def _generate_invoice_number(self) -> str:
        import random
        now = datetime.now()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        rand = random.randint(10000, 99999)
        number = f"INV-{year}{month}-{rand}"
        query = select(Invoice).where(Invoice.invoice_number == number)
        result = await self.db.execute(query)
        while result.scalar_one_or_none() is not None:
            rand = random.randint(10000, 99999)
            number = f"INV-{year}{month}-{rand}"
            query = select(Invoice).where(Invoice.invoice_number == number)
            result = await self.db.execute(query)
        return number
