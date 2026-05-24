from typing import Optional, List, Tuple
from uuid import UUID
from datetime import datetime, timezone
import random
import string
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.repositories.base import BaseRepository
from app.models.shipment import Shipment


class ShipmentRepository(BaseRepository[Shipment]):
    def __init__(self, session: AsyncSession):
        super().__init__(Shipment, session)

    async def get_by_tracking_number(self, tracking_number: str) -> Optional[Shipment]:
        query = select(Shipment).where(
            Shipment.tracking_number == tracking_number, Shipment.is_deleted == False
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_order(self, order_id: UUID) -> List[Shipment]:
        query = select(Shipment).where(
            Shipment.order_id == order_id, Shipment.is_deleted == False
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_status(
        self, status: str, skip: int = 0, limit: int = 20
    ) -> Tuple[List[Shipment], int]:
        q = select(Shipment).where(
            Shipment.status == status, Shipment.is_deleted == False
        ).offset(skip).limit(limit).order_by(Shipment.created_at.desc())
        count_q = select(func.count(Shipment.id)).where(
            Shipment.status == status, Shipment.is_deleted == False
        )
        result = await self.session.execute(q)
        items = list(result.scalars().all())
        total_result = await self.session.execute(count_q)
        total = total_result.scalar() or 0
        return items, total

    async def generate_tracking_number(self) -> str:
        year = datetime.now(timezone.utc).year
        suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"SHP-{year}-{suffix}"
