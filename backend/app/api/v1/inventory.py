from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_async_session
from app.core.dependencies import get_current_user, require_roles
from app.models.product import Product
from app.models.user import User
from app.models.warehouse import Warehouse
from app.schemas.common import APIResponse, PaginationParams, PaginationMeta
from app.schemas.inventory import InventoryCreate, InventoryUpdate, StockAdjustRequest
from app.services.inventory import InventoryService

router = APIRouter(prefix="/inventory", tags=["Inventory"])


async def serialize_inventory(item, db: AsyncSession):
    product = item.__dict__.get("product")
    warehouse = item.__dict__.get("warehouse")
    if product is None:
        product_result = await db.execute(select(Product.name, Product.sku).where(Product.id == item.product_id))
        product = product_result.first()
    if warehouse is None:
        warehouse_result = await db.execute(select(Warehouse.name).where(Warehouse.id == item.warehouse_id))
        warehouse = warehouse_result.first()
    product_name = product.name if product else ""
    product_sku = product.sku if product else ""
    warehouse_name = warehouse.name if warehouse else ""
    available_quantity = max((item.quantity or 0) - (item.reserved_quantity or 0), 0)
    return {
        "id": str(item.id),
        "product_id": str(item.product_id),
        "productId": str(item.product_id),
        "product_name": product_name,
        "productName": product_name,
        "product_sku": product_sku,
        "productSku": product_sku,
        "warehouse_id": str(item.warehouse_id),
        "warehouseId": str(item.warehouse_id),
        "warehouse_name": warehouse_name,
        "warehouseName": warehouse_name,
        "quantity": item.quantity,
        "reserved_quantity": item.reserved_quantity,
        "reservedQuantity": item.reserved_quantity,
        "available_quantity": available_quantity,
        "availableQuantity": available_quantity,
        "batch_number": item.batch_number,
        "batchNumber": item.batch_number,
        "expiry_date": item.expiry_date,
        "expiryDate": item.expiry_date,
        "last_count_date": item.last_count_date,
        "lastCountDate": item.last_count_date,
        "created_at": item.created_at,
        "updated_at": item.updated_at,
    }


@router.get("/")
async def list_inventory(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    search: str = Query(None),
    warehouse_id: str = Query(None),
    product_id: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    skip = (page - 1) * per_page
    params = PaginationParams(page=page, per_page=per_page, sort_by=sort_by, sort_order=sort_order)
    service = InventoryService(db)
    items, total = await service.list(params, skip=skip, search=search, warehouse_id=warehouse_id, product_id=product_id)
    total_pages = (total + per_page - 1) // per_page
    meta = PaginationMeta(
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )
    data = [await serialize_inventory(item, db) for item in items]
    return APIResponse(success=True, message="Inventory retrieved successfully", data=data, meta=meta)


@router.get("/low-stock/alerts")
async def get_low_stock_alerts(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    skip = (page - 1) * per_page
    service = InventoryService(db)
    items, total = await service.get_low_stock_alerts(skip=skip, per_page=per_page)
    total_pages = (total + per_page - 1) // per_page
    meta = PaginationMeta(
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )
    return APIResponse(success=True, message="Low stock alerts retrieved successfully", data=items, meta=meta)


@router.get("/by-warehouse/{warehouse_id}")
async def get_inventory_by_warehouse(
    warehouse_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    skip = (page - 1) * per_page
    service = InventoryService(db)
    items, total = await service.get_by_warehouse(warehouse_id, skip=skip, per_page=per_page)
    total_pages = (total + per_page - 1) // per_page
    meta = PaginationMeta(
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )
    data = [await serialize_inventory(item, db) for item in items]
    return APIResponse(success=True, message="Inventory by warehouse retrieved successfully", data=data, meta=meta)


@router.get("/by-product/{product_id}")
async def get_inventory_by_product(
    product_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    skip = (page - 1) * per_page
    service = InventoryService(db)
    items, total = await service.get_by_product(product_id, skip=skip, per_page=per_page)
    total_pages = (total + per_page - 1) // per_page
    meta = PaginationMeta(
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )
    data = [await serialize_inventory(item, db) for item in items]
    return APIResponse(success=True, message="Inventory by product retrieved successfully", data=data, meta=meta)


@router.get("/{inventory_id}")
async def get_inventory(
    inventory_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    service = InventoryService(db)
    data = await service.get_by_id(inventory_id)
    return APIResponse(success=True, message="Inventory item retrieved successfully", data=await serialize_inventory(data, db))


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_inventory(
    body: InventoryCreate,
    current_user: User = Depends(require_roles(["admin", "warehouse_manager"])),
    db: AsyncSession = Depends(get_async_session),
):
    service = InventoryService(db)
    data = await service.create(body)
    return APIResponse(success=True, message="Inventory created successfully", data=await serialize_inventory(data, db))


@router.api_route("/{inventory_id}", methods=["PATCH", "PUT"])
async def update_inventory(
    inventory_id: str,
    body: InventoryUpdate,
    current_user: User = Depends(require_roles(["admin", "warehouse_manager"])),
    db: AsyncSession = Depends(get_async_session),
):
    service = InventoryService(db)
    data = await service.update(inventory_id, body)
    return APIResponse(success=True, message="Inventory updated successfully", data=await serialize_inventory(data, db))


@router.delete("/{inventory_id}")
async def delete_inventory(
    inventory_id: str,
    current_user: User = Depends(require_roles(["admin"])),
    db: AsyncSession = Depends(get_async_session),
):
    service = InventoryService(db)
    await service.delete(inventory_id)
    return APIResponse(success=True, message="Inventory deleted successfully")


@router.post("/{inventory_id}/adjust")
async def adjust_stock(
    inventory_id: str,
    body: StockAdjustRequest,
    current_user: User = Depends(require_roles(["admin", "warehouse_manager"])),
    db: AsyncSession = Depends(get_async_session),
):
    service = InventoryService(db)
    data = await service.adjust_stock(inventory_id, body, current_user)
    return APIResponse(success=True, message="Stock adjusted successfully", data=await serialize_inventory(data, db))


@router.api_route("/{inventory_id}/stock", methods=["PATCH", "PUT"])
async def adjust_stock_legacy(
    inventory_id: str,
    body: StockAdjustRequest,
    current_user: User = Depends(require_roles(["admin", "warehouse_manager"])),
    db: AsyncSession = Depends(get_async_session),
):
    return await adjust_stock(inventory_id=inventory_id, body=body, current_user=current_user, db=db)
