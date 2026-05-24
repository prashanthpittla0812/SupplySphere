from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_async_session
from app.core.dependencies import get_current_user, require_roles
from app.models.user import User
from app.models.inventory import Inventory
from app.models.vendor import Vendor
from app.schemas.common import APIResponse, PaginationParams, PaginationMeta
from app.schemas.product import ProductCreate, ProductUpdate
from app.services.product import ProductService

router = APIRouter(prefix="/products", tags=["Products"])


async def serialize_product(product, db: AsyncSession):
    stock_result = await db.execute(
        select(func.coalesce(func.sum(Inventory.quantity), 0)).where(
            Inventory.product_id == product.id,
            Inventory.is_deleted == False,
        )
    )
    vendor_result = await db.execute(select(Vendor.name).where(Vendor.id == product.vendor_id))
    stock = float(stock_result.scalar() or 0)
    vendor_name = vendor_result.scalar() or ""
    return {
        "id": str(product.id),
        "name": product.name,
        "sku": product.sku,
        "description": product.description,
        "category": product.category,
        "unit_price": product.unit_price,
        "unitPrice": product.unit_price,
        "price": product.unit_price,
        "unit_cost": product.unit_cost,
        "unitCost": product.unit_cost,
        "tax_rate": product.tax_rate,
        "taxRate": product.tax_rate,
        "unit": product.unit,
        "min_stock_level": product.min_stock_level,
        "minStockLevel": product.min_stock_level,
        "reorderLevel": product.min_stock_level,
        "stock": stock,
        "image_url": product.image_url,
        "imageUrl": product.image_url,
        "is_active": product.is_active,
        "isActive": product.is_active,
        "vendor_id": str(product.vendor_id),
        "vendorId": str(product.vendor_id),
        "vendor_name": vendor_name,
        "vendorName": vendor_name,
        "vendor": vendor_name,
        "hsn_code": product.hsn_code,
        "hsnCode": product.hsn_code,
        "gst_rate": product.gst_rate,
        "gstRate": product.gst_rate,
        "created_at": product.created_at,
        "updated_at": product.updated_at,
    }


@router.get("/")
async def list_products(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    search: str = Query(None),
    category: str = Query(None),
    vendor_id: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    skip = (page - 1) * per_page
    params = PaginationParams(page=page, per_page=per_page, sort_by=sort_by, sort_order=sort_order)
    service = ProductService(db)
    items, total = await service.list(params, skip=skip, search=search, category=category, vendor_id=vendor_id)
    total_pages = (total + per_page - 1) // per_page
    meta = PaginationMeta(
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )
    data = [await serialize_product(item, db) for item in items]
    return APIResponse(success=True, message="Products retrieved successfully", data=data, meta=meta)


@router.get("/low-stock/list")
async def get_low_stock_products(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    skip = (page - 1) * per_page
    service = ProductService(db)
    items, total = await service.get_low_stock(skip=skip, per_page=per_page)
    total_pages = (total + per_page - 1) // per_page
    meta = PaginationMeta(
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )
    data = [await serialize_product(item, db) for item in items]
    return APIResponse(success=True, message="Low stock products retrieved successfully", data=data, meta=meta)


@router.get("/by-vendor/{vendor_id}")
async def get_products_by_vendor(
    vendor_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    skip = (page - 1) * per_page
    service = ProductService(db)
    items, total = await service.get_by_vendor(vendor_id, skip=skip, per_page=per_page)
    total_pages = (total + per_page - 1) // per_page
    meta = PaginationMeta(
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )
    data = [await serialize_product(item, db) for item in items]
    return APIResponse(success=True, message="Products by vendor retrieved successfully", data=data, meta=meta)


@router.get("/search")
async def search_products(
    q: str = Query(""),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    skip = (page - 1) * per_page
    params = PaginationParams(page=page, per_page=per_page, sort_by="created_at", sort_order="desc")
    service = ProductService(db)
    items, total = await service.list(params, skip=skip, search=q)
    data = [await serialize_product(item, db) for item in items]
    return APIResponse(success=True, message="Products searched successfully", data=data)


@router.get("/{product_id}")
async def get_product(
    product_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    service = ProductService(db)
    data = await service.get_by_id(product_id)
    return APIResponse(success=True, message="Product retrieved successfully", data=await serialize_product(data, db))


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_product(
    body: ProductCreate,
    current_user: User = Depends(require_roles(["admin", "warehouse_manager"])),
    db: AsyncSession = Depends(get_async_session),
):
    service = ProductService(db)
    data = await service.create(body)
    return APIResponse(success=True, message="Product created successfully", data=await serialize_product(data, db))


@router.api_route("/{product_id}", methods=["PATCH", "PUT"])
async def update_product(
    product_id: str,
    body: ProductUpdate,
    current_user: User = Depends(require_roles(["admin", "warehouse_manager"])),
    db: AsyncSession = Depends(get_async_session),
):
    service = ProductService(db)
    data = await service.update(product_id, body)
    return APIResponse(success=True, message="Product updated successfully", data=await serialize_product(data, db))


@router.delete("/{product_id}")
async def delete_product(
    product_id: str,
    current_user: User = Depends(require_roles(["admin"])),
    db: AsyncSession = Depends(get_async_session),
):
    service = ProductService(db)
    await service.delete(product_id)
    return APIResponse(success=True, message="Product deleted successfully")
