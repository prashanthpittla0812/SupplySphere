from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vendor import Vendor
from app.repositories.vendor import VendorRepository
from app.schemas.vendor import VendorCreate, VendorUpdate
from app.schemas.common import PaginationMeta
from app.core.exceptions import NotFoundException, ConflictException
from app.services.audit_log import AuditLogService


class VendorService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.vendor_repo = VendorRepository(db)
        self.audit_log_service = AuditLogService(db)

    def _uuid(self, value) -> UUID:
        return value if isinstance(value, UUID) else UUID(str(value))

    async def create_vendor(self, data: VendorCreate, user_id: UUID) -> Vendor:
        existing_email = await self.vendor_repo.get_by_email(data.email)
        if existing_email:
            raise ConflictException("Vendor with this email already exists")

        vendor = await self.vendor_repo.create(
            name=data.name,
            company_name=data.company_name,
            email=data.email,
            phone=data.phone,
            address=data.address,
            city=data.city,
            state=data.state,
            country=data.country,
            pincode=data.pincode,
            gst_number=data.gst_number,
            pan_number=data.pan_number,
            contact_person=data.contact_person,
            notes=data.notes,
            created_by=user_id,
        )
        return vendor

    async def create(self, data: VendorCreate, current_user) -> Vendor:
        return await self.create_vendor(data, current_user.id)

    async def update_vendor(self, vendor_id: UUID, data: VendorUpdate) -> Vendor:
        vendor_id = self._uuid(vendor_id)
        vendor = await self.vendor_repo.get_by_id(vendor_id)
        if not vendor:
            raise NotFoundException("Vendor not found")

        update_data = data.model_dump(exclude_unset=True)
        if "email" in update_data and update_data["email"]:
            existing = await self.vendor_repo.get_by_email(update_data["email"])
            if existing and existing.id != vendor_id:
                raise ConflictException("Email already in use")

        vendor = await self.vendor_repo.update(vendor_id, **update_data)
        return vendor

    async def update(self, vendor_id: UUID, data: VendorUpdate) -> Vendor:
        return await self.update_vendor(vendor_id, data)

    async def delete_vendor(self, vendor_id: UUID) -> bool:
        vendor_id = self._uuid(vendor_id)
        vendor = await self.vendor_repo.get_by_id(vendor_id)
        if not vendor:
            raise NotFoundException("Vendor not found")
        return await self.vendor_repo.soft_delete(vendor_id)

    async def delete(self, vendor_id: UUID) -> bool:
        return await self.delete_vendor(vendor_id)

    async def get_vendor(self, vendor_id: UUID) -> Vendor:
        vendor_id = self._uuid(vendor_id)
        vendor = await self.vendor_repo.get_by_id(vendor_id)
        if not vendor:
            raise NotFoundException("Vendor not found")
        return vendor

    async def get_by_id(self, vendor_id: UUID) -> Vendor:
        return await self.get_vendor(vendor_id)

    async def list(self, params, skip: int = 0, search: Optional[str] = None, **filters) -> Tuple[List[Vendor], int]:
        filters = {key: value for key, value in filters.items() if value is not None}
        return await self.vendor_repo.list_all(
            skip=skip,
            limit=params.per_page,
            sort_by=params.sort_by,
            sort_order=params.sort_order,
            filters=filters or None,
            search=search,
            search_fields=["name", "company_name", "email", "contact_person"],
        )

    async def approve(self, vendor_id: UUID) -> Vendor:
        return await self.approve_vendor(vendor_id)

    async def reject(self, vendor_id: UUID) -> Vendor:
        return await self.reject_vendor(vendor_id)

    async def list_vendors(
        self,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        status: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Tuple[List[Vendor], PaginationMeta]:
        filters = {}
        if status:
            filters["status"] = status

        skip = (page - 1) * per_page
        items, total = await self.vendor_repo.list_all(
            skip=skip,
            limit=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            filters=filters,
            search=search,
            search_fields=["name", "company_name", "email", "contact_person"],
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

    async def approve_vendor(self, vendor_id: UUID) -> Vendor:
        vendor_id = self._uuid(vendor_id)
        vendor = await self.vendor_repo.get_by_id(vendor_id)
        if not vendor:
            raise NotFoundException("Vendor not found")
        vendor = await self.vendor_repo.update(vendor_id, status="active")
        return vendor

    async def reject_vendor(self, vendor_id: UUID, reason: str = None) -> Vendor:
        vendor_id = self._uuid(vendor_id)
        vendor = await self.vendor_repo.get_by_id(vendor_id)
        if not vendor:
            raise NotFoundException("Vendor not found")
        vendor = await self.vendor_repo.update(vendor_id, status="rejected", notes=reason)
        return vendor

    async def search_vendors(
        self, query: str, page: int = 1, per_page: int = 20
    ) -> Tuple[List[Vendor], PaginationMeta]:
        skip = (page - 1) * per_page
        items, total = await self.vendor_repo.search(query, skip=skip, limit=per_page)
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
