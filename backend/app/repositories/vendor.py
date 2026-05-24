from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.repositories.base import BaseRepository
from app.models.vendor import Vendor


class VendorRepository(BaseRepository[Vendor]):
    def __init__(self, session: AsyncSession):
        super().__init__(Vendor, session)

    async def get_by_email(self, email: str) -> Optional[Vendor]:
        query = select(Vendor).where(Vendor.email == email, Vendor.is_deleted == False)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def search(
        self, query: str, skip: int = 0, limit: int = 20
    ) -> Tuple[List[Vendor], int]:
        search_filter = or_(
            Vendor.name.ilike(f"%{query}%"),
            Vendor.email.ilike(f"%{query}%"),
            Vendor.company_name.ilike(f"%{query}%"),
            Vendor.contact_person.ilike(f"%{query}%"),
        )
        q = select(Vendor).where(search_filter, Vendor.is_deleted == False).offset(skip).limit(limit).order_by(Vendor.created_at.desc())
        count_q = select(func.count(Vendor.id)).where(search_filter, Vendor.is_deleted == False)
        result = await self.session.execute(q)
        items = list(result.scalars().all())
        total_result = await self.session.execute(count_q)
        total = total_result.scalar() or 0
        return items, total

    async def get_by_status(self, status: str) -> List[Vendor]:
        query = select(Vendor).where(Vendor.status == status, Vendor.is_deleted == False)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_rating(self, vendor_id: UUID, new_rating: float) -> Optional[Vendor]:
        vendor = await self.get_by_id(vendor_id)
        if not vendor:
            return None
        vendor.rating = new_rating
        await self.session.flush()
        await self.session.refresh(vendor)
        return vendor
