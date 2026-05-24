from datetime import datetime, timezone
from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.shipment import Shipment
from app.schemas.common import PaginationMeta
from app.core.exceptions import NotFoundException


class ShipmentRepository:
    def __init__(self, session: AsyncSession):
        from app.repositories.base import BaseRepository
        self._repo = BaseRepository(Shipment, session)
        self.session = session

    async def get_by_id(self, id: UUID) -> Optional[Shipment]:
        id = id if isinstance(id, UUID) else UUID(str(id))
        return await self._repo.get_by_id(id)

    async def create(self, **kwargs) -> Shipment:
        return await self._repo.create(**kwargs)

    async def update(self, id: UUID, **kwargs) -> Optional[Shipment]:
        id = id if isinstance(id, UUID) else UUID(str(id))
        return await self._repo.update(id, **kwargs)

    async def soft_delete(self, id: UUID) -> bool:
        id = id if isinstance(id, UUID) else UUID(str(id))
        return await self._repo.soft_delete(id)

    async def list_all(self, **kwargs) -> Tuple[List[Shipment], int]:
        filters = kwargs.get("filters")
        if filters and "order_id" in filters and filters["order_id"] is not None and not isinstance(filters["order_id"], UUID):
            filters["order_id"] = UUID(str(filters["order_id"]))
        return await self._repo.list_all(**kwargs)

    async def get_by_order(self, order_id: UUID) -> List[Shipment]:
        order_id = order_id if isinstance(order_id, UUID) else UUID(str(order_id))
        query = select(Shipment).where(Shipment.order_id == order_id, Shipment.is_deleted == False)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_tracking(self, tracking_number: str) -> Optional[Shipment]:
        query = select(Shipment).where(Shipment.tracking_number == tracking_number, Shipment.is_deleted == False)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


class ShipmentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.shipment_repo = ShipmentRepository(db)

    def _uuid(self, value) -> UUID:
        return value if isinstance(value, UUID) else UUID(str(value))

    async def create_shipment(self, data) -> Shipment:
        tracking_number = await self._generate_tracking_number()

        shipment = await self.shipment_repo.create(
            tracking_number=tracking_number,
            order_id=data.order_id,
            carrier=data.carrier,
            origin_warehouse_id=data.origin_warehouse_id,
            destination_address=data.destination_address,
            estimated_delivery=getattr(data, 'estimated_delivery', None),
            weight=getattr(data, 'weight', None),
            dimensions=getattr(data, 'dimensions', None),
            notes=getattr(data, 'notes', None),
            status="pending",
            last_updated=datetime.now(timezone.utc),
        )
        return shipment

    async def create(self, data) -> Shipment:
        return await self.create_shipment(data)

    async def update_shipment(self, shipment_id: UUID, data) -> Shipment:
        shipment_id = self._uuid(shipment_id)
        shipment = await self.shipment_repo.get_by_id(shipment_id)
        if not shipment:
            raise NotFoundException("Shipment not found")

        update_data = data.model_dump(exclude_unset=True)
        shipment = await self.shipment_repo.update(shipment_id, **update_data)
        return shipment

    async def update(self, shipment_id: UUID, data) -> Shipment:
        return await self.update_shipment(shipment_id, data)

    async def delete_shipment(self, shipment_id: UUID) -> bool:
        shipment_id = self._uuid(shipment_id)
        shipment = await self.shipment_repo.get_by_id(shipment_id)
        if not shipment:
            raise NotFoundException("Shipment not found")
        return await self.shipment_repo.soft_delete(shipment_id)

    async def delete(self, shipment_id: UUID) -> bool:
        return await self.delete_shipment(shipment_id)

    async def get_shipment(self, shipment_id: UUID) -> Shipment:
        shipment_id = self._uuid(shipment_id)
        shipment = await self.shipment_repo.get_by_id(shipment_id)
        if not shipment:
            raise NotFoundException("Shipment not found")
        return shipment

    async def get_by_id(self, shipment_id: UUID) -> Shipment:
        return await self.get_shipment(shipment_id)

    async def list(self, params, skip: int = 0, search: Optional[str] = None, **filters) -> Tuple[List[Shipment], int]:
        filters = {key: value for key, value in filters.items() if value is not None}
        if "order_id" in filters:
            filters["order_id"] = self._uuid(filters["order_id"])
        return await self.shipment_repo.list_all(
            skip=skip,
            limit=params.per_page,
            sort_by=params.sort_by,
            sort_order=params.sort_order,
            filters=filters or None,
            search=search,
            search_fields=["tracking_number", "carrier", "destination_address"],
        )

    async def list_shipments(
        self,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        status: Optional[str] = None,
        carrier: Optional[str] = None,
        order_id: Optional[UUID] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Tuple[List[Shipment], PaginationMeta]:
        filters = {}
        if status:
            filters["status"] = status
        if carrier:
            filters["carrier"] = carrier
        if order_id:
            filters["order_id"] = order_id

        skip = (page - 1) * per_page
        items, total = await self.shipment_repo.list_all(
            skip=skip,
            limit=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            filters=filters,
            search=search,
            search_fields=["tracking_number", "carrier", "destination_address"],
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

    async def update_tracking(self, shipment_id: UUID, location, status: str = None) -> Shipment:
        shipment_id = self._uuid(shipment_id)
        shipment = await self.shipment_repo.get_by_id(shipment_id)
        if not shipment:
            raise NotFoundException("Shipment not found")
        if hasattr(location, "location"):
            status = location.status
            location = location.location or getattr(location, "current_location", None)

        shipment = await self.shipment_repo.update(
            shipment_id,
            current_location=location,
            status=status,
            last_updated=datetime.now(timezone.utc),
        )
        return shipment

    async def get_shipments_by_order(self, order_id: UUID) -> List[Shipment]:
        order_id = self._uuid(order_id)
        return await self.shipment_repo.get_by_order(order_id)

    async def get_by_order(self, order_id: UUID, skip: int = 0, per_page: int = 20) -> Tuple[List[Shipment], int]:
        items = await self.get_shipments_by_order(order_id)
        return items[skip : skip + per_page], len(items)

    async def _generate_tracking_number(self) -> str:
        import uuid
        return f"SH-{uuid.uuid4().hex[:12].upper()}"
