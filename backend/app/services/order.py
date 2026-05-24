from datetime import datetime, timezone
from typing import Optional, List, Tuple, Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.order import PurchaseOrder, PurchaseOrderItem
from app.models.product import Product
from app.repositories.product import ProductRepository
from app.repositories.vendor import VendorRepository
from app.schemas.common import PaginationMeta
from app.core.exceptions import NotFoundException, BadRequestException
from app.services.audit_log import AuditLogService


class OrderRepository:
    def __init__(self, session: AsyncSession):
        from app.repositories.base import BaseRepository
        self._repo = BaseRepository(PurchaseOrder, session)
        self.session = session

    async def get_by_id(self, id: UUID) -> Optional[PurchaseOrder]:
        from sqlalchemy.orm import selectinload
        id = id if isinstance(id, UUID) else UUID(str(id))
        query = (
            select(PurchaseOrder)
            .where(PurchaseOrder.id == id, PurchaseOrder.is_deleted == False)
            .options(selectinload(PurchaseOrder.items))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, **kwargs) -> PurchaseOrder:
        instance = PurchaseOrder(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def update(self, id: UUID, **kwargs) -> Optional[PurchaseOrder]:
        id = id if isinstance(id, UUID) else UUID(str(id))
        instance = await self.get_by_id(id)
        if not instance:
            return None
        for key, value in kwargs.items():
            if value is not None and hasattr(instance, key):
                setattr(instance, key, value)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def soft_delete(self, id: UUID) -> bool:
        id = id if isinstance(id, UUID) else UUID(str(id))
        instance = await self.get_by_id(id)
        if not instance:
            return False
        instance.is_deleted = True
        instance.deleted_at = datetime.now(timezone.utc)
        await self.session.flush()
        return True

    async def list_all(self, **kwargs) -> Tuple[List[PurchaseOrder], int]:
        from app.repositories.base import BaseRepository
        filters = kwargs.get("filters")
        if filters and "vendor_id" in filters and filters["vendor_id"] is not None and not isinstance(filters["vendor_id"], UUID):
            filters["vendor_id"] = UUID(str(filters["vendor_id"]))
        base = BaseRepository(PurchaseOrder, self.session)
        return await base.list_all(**kwargs)

    async def get_by_vendor(self, vendor_id: UUID) -> List[PurchaseOrder]:
        vendor_id = vendor_id if isinstance(vendor_id, UUID) else UUID(str(vendor_id))
        query = select(PurchaseOrder).where(PurchaseOrder.vendor_id == vendor_id, PurchaseOrder.is_deleted == False)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_status_distribution(self) -> List[Dict[str, Any]]:
        query = select(
            PurchaseOrder.status,
            func.count(PurchaseOrder.id).label("count"),
        ).where(PurchaseOrder.is_deleted == False).group_by(PurchaseOrder.status)
        result = await self.session.execute(query)
        rows = result.all()
        return [{"status": row.status, "count": row.count} for row in rows]

    async def get_monthly_trends(self, months: int = 12) -> List[Dict[str, Any]]:
        from sqlalchemy import extract
        cutoff = datetime.now(timezone.utc) - __import__('datetime', fromlist=['']).timedelta(days=30 * months)
        query = select(
            extract('year', PurchaseOrder.created_at).label("year"),
            extract('month', PurchaseOrder.created_at).label("month"),
            func.count(PurchaseOrder.id).label("count"),
            func.coalesce(func.sum(PurchaseOrder.total_amount), 0).label("revenue"),
        ).where(
            PurchaseOrder.is_deleted == False,
            PurchaseOrder.created_at >= cutoff,
        ).group_by("year", "month").order_by("year", "month")
        result = await self.session.execute(query)
        rows = result.all()
        return [
            {"year": int(row.year), "month": int(row.month), "count": row.count, "revenue": float(row.revenue)}
            for row in rows
        ]

    async def get_recent_orders(self, limit: int = 10) -> List[PurchaseOrder]:
        query = select(PurchaseOrder).where(PurchaseOrder.is_deleted == False).order_by(PurchaseOrder.created_at.desc()).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())


class OrderItemRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def bulk_create(self, items: List[Dict[str, Any]]) -> List[PurchaseOrderItem]:
        instances = [PurchaseOrderItem(**item) for item in items]
        self.session.add_all(instances)
        await self.session.flush()
        return instances


class OrderService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.order_repo = OrderRepository(db)
        self.order_item_repo = OrderItemRepository(db)
        self.product_repo = ProductRepository(db)
        self.vendor_repo = VendorRepository(db)
        self.audit_log_service = AuditLogService(db)

    def _uuid(self, value) -> UUID:
        return value if isinstance(value, UUID) else UUID(str(value))

    async def create_order(self, data, user_id: UUID) -> PurchaseOrder:
        vendor = await self.vendor_repo.get_by_id(data.vendor_id)
        if not vendor:
            raise NotFoundException("Vendor not found")

        order_number = await self.generate_order_number()
        total_amount = 0.0
        order_items_data = []

        for item in data.items:
            product = await self.product_repo.get_by_id(item.product_id)
            if not product:
                raise NotFoundException(f"Product {item.product_id} not found")

            unit_price = item.unit_price if hasattr(item, 'unit_price') and item.unit_price else product.unit_price
            total_price = unit_price * item.quantity
            total_amount += total_price

            order_items_data.append({
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": unit_price,
                "total_price": total_price,
            })

        order = await self.order_repo.create(
            order_number=order_number,
            vendor_id=data.vendor_id,
            warehouse_id=getattr(data, "warehouse_id", None),
            status="pending",
            subtotal=total_amount,
            total_amount=total_amount,
            ordered_by=getattr(user_id, "id", user_id),
            created_by=getattr(user_id, "id", user_id),
            priority=getattr(data, 'priority', None),
            is_urgent=getattr(data, 'is_urgent', False),
            notes=getattr(data, 'notes', None),
            terms=getattr(data, "terms", None),
            expected_delivery_date=getattr(data, "expected_delivery_date", None),
            discount=getattr(data, "discount", 0.0),
            currency=getattr(data, "currency", "INR"),
        )

        for item_data in order_items_data:
            item_data["order_id"] = order.id
        await self.order_item_repo.bulk_create(order_items_data)

        await self.audit_log_service.log_action(
            user_id=user_id,
            action="create_order",
            entity_type="purchase_order",
            entity_id=order.id,
            changes={"order_number": order_number, "total_amount": total_amount},
            ip_address=None,
            user_agent=None,
            description=f"Order {order_number} created",
        )

        from sqlalchemy.orm import selectinload
        query = (
            select(PurchaseOrder)
            .where(PurchaseOrder.id == order.id)
            .options(selectinload(PurchaseOrder.items))
        )
        result = await self.db.execute(query)
        return result.scalar_one()

    async def create(self, data, current_user) -> PurchaseOrder:
        return await self.create_order(data, getattr(current_user, "id", current_user))

    async def update_order(self, order_id: UUID, data) -> PurchaseOrder:
        order_id = self._uuid(order_id)
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise NotFoundException("Order not found")

        update_data = data.model_dump(exclude_unset=True)
        order = await self.order_repo.update(order_id, **update_data)
        return order

    async def update(self, order_id: UUID, data) -> PurchaseOrder:
        return await self.update_order(order_id, data)

    async def delete_order(self, order_id: UUID) -> bool:
        order_id = self._uuid(order_id)
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise NotFoundException("Order not found")
        return await self.order_repo.soft_delete(order_id)

    async def delete(self, order_id: UUID) -> bool:
        return await self.delete_order(order_id)

    async def get_order(self, order_id: UUID) -> PurchaseOrder:
        order_id = self._uuid(order_id)
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise NotFoundException("Order not found")
        return order

    async def get_by_id(self, order_id: UUID) -> PurchaseOrder:
        return await self.get_order(order_id)

    async def list(self, params, skip: int = 0, search: Optional[str] = None, **filters) -> Tuple[List[PurchaseOrder], int]:
        filters = {key: value for key, value in filters.items() if value is not None}
        if "vendor_id" in filters:
            filters["vendor_id"] = self._uuid(filters["vendor_id"])
        return await self.order_repo.list_all(
            skip=skip,
            limit=params.per_page,
            sort_by=params.sort_by,
            sort_order=params.sort_order,
            filters=filters or None,
            search=search,
            search_fields=["order_number"],
        )

    async def list_orders(
        self,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        status: Optional[str] = None,
        vendor_id: Optional[UUID] = None,
        priority: Optional[str] = None,
        is_urgent: Optional[bool] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Tuple[List[PurchaseOrder], PaginationMeta]:
        filters = {}
        if status:
            filters["status"] = status
        if vendor_id:
            filters["vendor_id"] = vendor_id
        if priority:
            filters["priority"] = priority
        if is_urgent is not None:
            filters["is_urgent"] = is_urgent

        skip = (page - 1) * per_page
        items, total = await self.order_repo.list_all(
            skip=skip,
            limit=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            filters=filters,
            search=search,
            search_fields=["order_number"],
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

    async def approve_order(self, order_id: UUID, user_id: UUID, data) -> PurchaseOrder:
        order_id = self._uuid(order_id)
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise NotFoundException("Order not found")
        if order.status != "pending":
            raise BadRequestException("Only pending orders can be approved")

        order = await self.order_repo.update(
            order_id,
            status="approved",
            approved_by=getattr(user_id, "id", user_id),
            approved_at=datetime.now(timezone.utc),
        )
        return order

    async def approve(self, order_id: UUID, data, current_user) -> PurchaseOrder:
        return await self.approve_order(order_id, getattr(current_user, "id", current_user), data)

    async def get_orders_by_vendor(self, vendor_id: UUID) -> List[PurchaseOrder]:
        vendor_id = self._uuid(vendor_id)
        return await self.order_repo.get_by_vendor(vendor_id)

    async def get_by_vendor(self, vendor_id: UUID, skip: int = 0, per_page: int = 20) -> Tuple[List[PurchaseOrder], int]:
        items = await self.order_repo.get_by_vendor(vendor_id)
        return items[skip : skip + per_page], len(items)

    async def get_order_status_distribution(self) -> List[Dict[str, Any]]:
        return await self.order_repo.get_status_distribution()

    async def get_status_distribution(self) -> List[Dict[str, Any]]:
        return await self.get_order_status_distribution()

    async def get_monthly_trends(self, months: int = 12, year: Optional[int] = None) -> List[Dict[str, Any]]:
        return await self.order_repo.get_monthly_trends(months)

    async def get_recent_orders(self, limit: int = 10) -> List[PurchaseOrder]:
        return await self.order_repo.get_recent_orders(limit)

    async def get_recent(self, limit: int = 10) -> List[PurchaseOrder]:
        return await self.get_recent_orders(limit)

    async def generate_order_number(self) -> str:
        import random
        from app.core.config import settings
        now = datetime.now()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        rand = random.randint(10000, 99999)
        number = f"PO-{year}{month}-{rand}"
        query = select(PurchaseOrder).where(PurchaseOrder.order_number == number)
        result = await self.db.execute(query)
        while result.scalar_one_or_none() is not None:
            rand = random.randint(10000, 99999)
            number = f"PO-{year}{month}-{rand}"
            query = select(PurchaseOrder).where(PurchaseOrder.order_number == number)
            result = await self.db.execute(query)
        return number
