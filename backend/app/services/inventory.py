from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.inventory import Inventory
from app.models.product import Product
from app.repositories.product import ProductRepository
from app.schemas.common import PaginationMeta
from app.core.exceptions import NotFoundException
from app.services.audit_log import AuditLogService


class InventoryRepository:
    def __init__(self, session: AsyncSession):
        from app.repositories.base import BaseRepository
        self._repo = BaseRepository(Inventory, session)
        self.session = session

    async def get_by_id(self, id: UUID) -> Optional[Inventory]:
        id = id if isinstance(id, UUID) else UUID(str(id))
        return await self._repo.get_by_id(id)

    async def create(self, **kwargs) -> Inventory:
        return await self._repo.create(**kwargs)

    async def update(self, id: UUID, **kwargs) -> Optional[Inventory]:
        id = id if isinstance(id, UUID) else UUID(str(id))
        return await self._repo.update(id, **kwargs)

    async def soft_delete(self, id: UUID) -> bool:
        id = id if isinstance(id, UUID) else UUID(str(id))
        return await self._repo.soft_delete(id)

    async def list_all(self, **kwargs) -> Tuple[List[Inventory], int]:
        filters = kwargs.get("filters")
        if filters:
            for key in ("id", "product_id", "warehouse_id"):
                if key in filters and filters[key] is not None and not isinstance(filters[key], UUID):
                    filters[key] = UUID(str(filters[key]))
        return await self._repo.list_all(**kwargs)

    async def get_by_warehouse(self, warehouse_id: UUID) -> List[Inventory]:
        from sqlalchemy import select
        warehouse_id = warehouse_id if isinstance(warehouse_id, UUID) else UUID(str(warehouse_id))
        query = select(Inventory).options(selectinload(Inventory.product), selectinload(Inventory.warehouse)).where(Inventory.warehouse_id == warehouse_id, Inventory.is_deleted == False)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_product(self, product_id: UUID) -> List[Inventory]:
        from sqlalchemy import select
        product_id = product_id if isinstance(product_id, UUID) else UUID(str(product_id))
        query = select(Inventory).options(selectinload(Inventory.product), selectinload(Inventory.warehouse)).where(Inventory.product_id == product_id, Inventory.is_deleted == False)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_low_stock_alerts(self) -> List[Inventory]:
        from sqlalchemy import select, func
        subq = (
            select(Inventory.product_id, func.sum(Inventory.quantity).label("total_qty"))
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
        low_stock_products = list(result.scalars().all())
        if not low_stock_products:
            return []
        product_ids = [p.id for p in low_stock_products]
        q = select(Inventory).where(Inventory.product_id.in_(product_ids), Inventory.is_deleted == False)
        r = await self.session.execute(q)
        return list(r.scalars().all())

    async def get_product_quantity(self, product_id: UUID) -> float:
        from sqlalchemy import select, func
        query = select(func.coalesce(func.sum(Inventory.quantity), 0)).where(
            Inventory.product_id == product_id, Inventory.is_deleted == False
        )
        result = await self.session.execute(query)
        return result.scalar() or 0.0


class InventoryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.inventory_repo = InventoryRepository(db)
        self.product_repo = ProductRepository(db)
        self.audit_log_service = AuditLogService(db)

    def _uuid(self, value) -> UUID:
        return value if isinstance(value, UUID) else UUID(str(value))

    async def create_inventory(self, data) -> Inventory:
        product = await self.product_repo.get_by_id(data.product_id)
        if not product:
            raise NotFoundException("Product not found")

        inventory = await self.inventory_repo.create(
            product_id=data.product_id,
            warehouse_id=data.warehouse_id,
            quantity=data.quantity,
            reserved_quantity=data.reserved_quantity if hasattr(data, 'reserved_quantity') else 0.0,
            batch_number=data.batch_number if hasattr(data, 'batch_number') else None,
            expiry_date=data.expiry_date if hasattr(data, 'expiry_date') else None,
            last_count_date=data.last_count_date if hasattr(data, 'last_count_date') else None,
        )
        return inventory

    async def create(self, data) -> Inventory:
        return await self.create_inventory(data)

    async def update_inventory(self, inventory_id: UUID, data) -> Inventory:
        inventory_id = self._uuid(inventory_id)
        inventory = await self.inventory_repo.get_by_id(inventory_id)
        if not inventory:
            raise NotFoundException("Inventory record not found")

        update_data = data.model_dump(exclude_unset=True)
        inventory = await self.inventory_repo.update(inventory_id, **update_data)
        return inventory

    async def update(self, inventory_id: UUID, data) -> Inventory:
        return await self.update_inventory(inventory_id, data)

    async def delete_inventory(self, inventory_id: UUID) -> bool:
        inventory_id = self._uuid(inventory_id)
        inventory = await self.inventory_repo.get_by_id(inventory_id)
        if not inventory:
            raise NotFoundException("Inventory record not found")
        return await self.inventory_repo.soft_delete(inventory_id)

    async def delete(self, inventory_id: UUID) -> bool:
        return await self.delete_inventory(inventory_id)

    async def get_inventory(self, inventory_id: UUID) -> Inventory:
        inventory_id = self._uuid(inventory_id)
        inventory = await self.inventory_repo.get_by_id(inventory_id)
        if not inventory:
            raise NotFoundException("Inventory record not found")
        return inventory

    async def get_by_id(self, inventory_id: UUID) -> Inventory:
        return await self.get_inventory(inventory_id)

    async def list(self, params, skip: int = 0, search: Optional[str] = None, **filters) -> Tuple[List[Inventory], int]:
        filters = {key: value for key, value in filters.items() if value is not None}
        for key in ("product_id", "warehouse_id"):
            if key in filters:
                filters[key] = self._uuid(filters[key])
        return await self.inventory_repo.list_all(
            skip=skip,
            limit=params.per_page,
            sort_by=params.sort_by,
            sort_order=params.sort_order,
            filters=filters or None,
        )

    async def get_by_warehouse(self, warehouse_id: UUID, skip: int = 0, per_page: int = 20) -> Tuple[List[Inventory], int]:
        items = await self.get_inventory_by_warehouse(warehouse_id)
        return items[skip : skip + per_page], len(items)

    async def get_by_product(self, product_id: UUID, skip: int = 0, per_page: int = 20) -> Tuple[List[Inventory], int]:
        items = await self.get_inventory_by_product(product_id)
        return items[skip : skip + per_page], len(items)

    async def list_inventory(
        self,
        page: int = 1,
        per_page: int = 20,
        product_id: Optional[UUID] = None,
        warehouse_id: Optional[UUID] = None,
        low_stock_only: bool = False,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Tuple[List[Inventory], PaginationMeta]:
        filters = {}
        if product_id:
            filters["product_id"] = product_id
        if warehouse_id:
            filters["warehouse_id"] = warehouse_id

        skip = (page - 1) * per_page
        items, total = await self.inventory_repo.list_all(
            skip=skip,
            limit=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            filters=filters,
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

    async def adjust_stock(self, inventory_id: UUID, data, user_id: UUID) -> Inventory:
        inventory_id = self._uuid(inventory_id)
        inventory = await self.inventory_repo.get_by_id(inventory_id)
        if not inventory:
            raise NotFoundException("Inventory record not found")

        requested_quantity = data.quantity if hasattr(data, 'quantity') else data.get('quantity')
        adjustment_type = getattr(data, "adjustment_type", None) or data.get("type", "set")
        if adjustment_type == "add":
            new_quantity = inventory.quantity + requested_quantity
        elif adjustment_type in {"subtract", "remove"}:
            new_quantity = max(inventory.quantity - requested_quantity, 0.0)
        else:
            new_quantity = requested_quantity
        inventory = await self.inventory_repo.update(inventory_id, quantity=new_quantity, last_count_date=None)

        await self.audit_log_service.log_action(
            user_id=getattr(user_id, "id", user_id),
            action="stock_adjustment",
            entity_type="inventory",
            entity_id=inventory_id,
            changes={"new_quantity": new_quantity},
            ip_address=None,
            user_agent=None,
            description=f"Stock adjusted to {new_quantity}",
        )
        return inventory

    async def get_low_stock_alerts(self, skip: int = 0, per_page: Optional[int] = None):
        items = await self.inventory_repo.get_low_stock_alerts()
        if per_page is not None:
            return items[skip : skip + per_page], len(items)
        return items

    async def get_inventory_by_warehouse(self, warehouse_id: UUID) -> List[Inventory]:
        warehouse_id = self._uuid(warehouse_id)
        return await self.inventory_repo.get_by_warehouse(warehouse_id)

    async def get_inventory_by_product(self, product_id: UUID) -> List[Inventory]:
        product_id = self._uuid(product_id)
        return await self.inventory_repo.get_by_product(product_id)
