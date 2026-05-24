from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.warehouse import Warehouse
from app.schemas.common import PaginationMeta
from app.core.exceptions import NotFoundException
from app.services.audit_log import AuditLogService


class WarehouseRepository:
    def __init__(self, session: AsyncSession):
        from app.repositories.base import BaseRepository
        self._repo = BaseRepository(Warehouse, session)
        self.session = session

    async def get_by_id(self, id: UUID) -> Optional[Warehouse]:
        id = id if isinstance(id, UUID) else UUID(str(id))
        return await self._repo.get_by_id(id)

    async def create(self, **kwargs) -> Warehouse:
        return await self._repo.create(**kwargs)

    async def update(self, id: UUID, **kwargs) -> Optional[Warehouse]:
        id = id if isinstance(id, UUID) else UUID(str(id))
        return await self._repo.update(id, **kwargs)

    async def soft_delete(self, id: UUID) -> bool:
        id = id if isinstance(id, UUID) else UUID(str(id))
        return await self._repo.soft_delete(id)

    async def list_all(self, **kwargs) -> Tuple[List[Warehouse], int]:
        return await self._repo.list_all(**kwargs)

    async def get_available(self) -> List[Warehouse]:
        from sqlalchemy import select
        query = select(Warehouse).where(Warehouse.is_deleted == False, Warehouse.status == "active")
        result = await self.session.execute(query)
        return list(result.scalars().all())


class WarehouseService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.warehouse_repo = WarehouseRepository(db)
        self.audit_log_service = AuditLogService(db)

    def _uuid(self, value) -> UUID:
        return value if isinstance(value, UUID) else UUID(str(value))

    async def create_warehouse(self, data) -> Warehouse:
        warehouse = await self.warehouse_repo.create(
            name=data.name,
            code=data.code if hasattr(data, 'code') else None,
            address=data.address,
            city=data.city,
            state=data.state,
            country=data.country,
            pincode=data.pincode,
            capacity=data.capacity if hasattr(data, 'capacity') else None,
            status=data.status if hasattr(data, 'status') else "active",
            manager_id=getattr(data, "manager_id", None),
            latitude=getattr(data, "latitude", None),
            longitude=getattr(data, "longitude", None),
        )
        return warehouse

    async def create(self, data) -> Warehouse:
        return await self.create_warehouse(data)

    async def update_warehouse(self, warehouse_id: UUID, data) -> Warehouse:
        warehouse_id = self._uuid(warehouse_id)
        warehouse = await self.warehouse_repo.get_by_id(warehouse_id)
        if not warehouse:
            raise NotFoundException("Warehouse not found")

        update_data = data.model_dump(exclude_unset=True)
        warehouse = await self.warehouse_repo.update(warehouse_id, **update_data)
        return warehouse

    async def update(self, warehouse_id: UUID, data) -> Warehouse:
        return await self.update_warehouse(warehouse_id, data)

    async def delete_warehouse(self, warehouse_id: UUID) -> bool:
        warehouse_id = self._uuid(warehouse_id)
        warehouse = await self.warehouse_repo.get_by_id(warehouse_id)
        if not warehouse:
            raise NotFoundException("Warehouse not found")
        return await self.warehouse_repo.soft_delete(warehouse_id)

    async def delete(self, warehouse_id: UUID) -> bool:
        return await self.delete_warehouse(warehouse_id)

    async def get_warehouse(self, warehouse_id: UUID) -> Warehouse:
        warehouse_id = self._uuid(warehouse_id)
        warehouse = await self.warehouse_repo.get_by_id(warehouse_id)
        if not warehouse:
            raise NotFoundException("Warehouse not found")
        return warehouse

    async def get_by_id(self, warehouse_id: UUID) -> Warehouse:
        return await self.get_warehouse(warehouse_id)

    async def list(self, params, skip: int = 0, search: Optional[str] = None, **filters) -> Tuple[List[Warehouse], int]:
        filters = {key: value for key, value in filters.items() if value is not None}
        return await self.warehouse_repo.list_all(
            skip=skip,
            limit=params.per_page,
            sort_by=params.sort_by,
            sort_order=params.sort_order,
            filters=filters or None,
            search=search,
            search_fields=["name", "code", "city", "state", "country"],
        )

    async def get_available(self, skip: int = 0, per_page: int = 20) -> Tuple[List[Warehouse], int]:
        items = await self.get_available_warehouses()
        return items[skip : skip + per_page], len(items)

    async def list_warehouses(
        self,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        status: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Tuple[List[Warehouse], PaginationMeta]:
        filters = {}
        if status:
            filters["status"] = status

        skip = (page - 1) * per_page
        items, total = await self.warehouse_repo.list_all(
            skip=skip,
            limit=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            filters=filters,
            search=search,
            search_fields=["name", "code", "city", "state", "country"],
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

    async def get_available_warehouses(self) -> List[Warehouse]:
        return await self.warehouse_repo.get_available()
