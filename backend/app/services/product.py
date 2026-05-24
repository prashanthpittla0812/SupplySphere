from typing import Optional, List, Tuple, Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.repositories.product import ProductRepository
from app.schemas.common import PaginationMeta
from app.core.exceptions import NotFoundException, ConflictException
from app.services.audit_log import AuditLogService


class ProductService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.product_repo = ProductRepository(db)
        self.audit_log_service = AuditLogService(db)

    def _uuid(self, value) -> UUID:
        return value if isinstance(value, UUID) else UUID(str(value))

    async def create_product(self, data) -> Product:
        existing_sku = await self.product_repo.get_by_sku(data.sku)
        if existing_sku:
            raise ConflictException("Product with this SKU already exists")

        product = await self.product_repo.create(
            name=data.name,
            sku=data.sku,
            description=data.description,
            category=data.category,
            unit_price=data.unit_price,
            unit_cost=data.unit_cost,
            tax_rate=data.tax_rate,
            hsn_code=getattr(data, "hsn_code", None),
            gst_rate=getattr(data, "gst_rate", None),
            unit=data.unit,
            min_stock_level=data.min_stock_level,
            image_url=data.image_url,
            is_active=getattr(data, "is_active", True),
            vendor_id=data.vendor_id,
        )
        return product

    async def create(self, data) -> Product:
        return await self.create_product(data)

    async def update_product(self, product_id: UUID, data) -> Product:
        product_id = self._uuid(product_id)
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise NotFoundException("Product not found")

        update_data = data.model_dump(exclude_unset=True)
        if "sku" in update_data and update_data["sku"]:
            existing = await self.product_repo.get_by_sku(update_data["sku"])
            if existing and existing.id != product_id:
                raise ConflictException("SKU already in use")

        product = await self.product_repo.update(product_id, **update_data)
        return product

    async def update(self, product_id: UUID, data) -> Product:
        return await self.update_product(product_id, data)

    async def delete_product(self, product_id: UUID) -> bool:
        product_id = self._uuid(product_id)
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise NotFoundException("Product not found")
        return await self.product_repo.soft_delete(product_id)

    async def delete(self, product_id: UUID) -> bool:
        return await self.delete_product(product_id)

    async def get_product(self, product_id: UUID) -> Product:
        product_id = self._uuid(product_id)
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise NotFoundException("Product not found")
        return product

    async def get_by_id(self, product_id: UUID) -> Product:
        return await self.get_product(product_id)

    async def list(self, params, skip: int = 0, search: Optional[str] = None, **filters) -> Tuple[List[Product], int]:
        filters = {key: value for key, value in filters.items() if value is not None}
        return await self.product_repo.list_all(
            skip=skip,
            limit=params.per_page,
            sort_by=params.sort_by,
            sort_order=params.sort_order,
            filters=filters or None,
            search=search,
            search_fields=["name", "sku", "category", "description"],
        )

    async def get_by_vendor(self, vendor_id: UUID, skip: int = 0, per_page: int = 20) -> Tuple[List[Product], int]:
        vendor_id = self._uuid(vendor_id)
        return await self.product_repo.list_all(skip=skip, limit=per_page, filters={"vendor_id": vendor_id})

    async def get_low_stock(self, skip: int = 0, per_page: int = 20) -> Tuple[List[Product], int]:
        items = await self.get_low_stock_products()
        return items[skip : skip + per_page], len(items)

    async def list_products(
        self,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        category: Optional[str] = None,
        vendor_id: Optional[UUID] = None,
        is_active: Optional[bool] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Tuple[List[Product], PaginationMeta]:
        filters = {}
        if category:
            filters["category"] = category
        if vendor_id:
            filters["vendor_id"] = vendor_id
        if is_active is not None:
            filters["is_active"] = is_active

        skip = (page - 1) * per_page
        items, total = await self.product_repo.list_all(
            skip=skip,
            limit=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            filters=filters,
            search=search,
            search_fields=["name", "sku", "category", "description"],
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

    async def get_products_by_vendor(self, vendor_id: UUID) -> List[Product]:
        return await self.product_repo.get_by_vendor(vendor_id)

    async def get_low_stock_products(self) -> List[Product]:
        return await self.product_repo.get_low_stock_products()

    async def get_category_breakdown(self) -> List[Dict[str, Any]]:
        return await self.product_repo.get_category_breakdown()
