from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_async_session
from app.core.dependencies import get_current_user, require_roles
from app.models.user import User
from app.models.order import PurchaseOrderItem
from app.schemas.common import APIResponse, PaginationParams, PaginationMeta
from app.schemas.order import OrderCreate, OrderUpdate, OrderApproval
from app.services.order import OrderService

router = APIRouter(prefix="/orders", tags=["Orders"])


async def serialize_order(order, db: AsyncSession):
    items = order.__dict__.get("items")
    if items is None:
        count_result = await db.execute(
            select(func.count(PurchaseOrderItem.id)).where(
                PurchaseOrderItem.order_id == order.id,
                PurchaseOrderItem.is_deleted == False,
            )
        )
        item_count = count_result.scalar() or 0
    else:
        item_count = len([item for item in items if not item.is_deleted])
    expected_delivery = order.expected_delivery_date or order.delivered_date or order.created_at
    return {
        "id": str(order.id),
        "order_number": order.order_number,
        "orderNumber": order.order_number,
        "vendor_id": str(order.vendor_id),
        "vendorId": str(order.vendor_id),
        "vendor_name": order.vendor_name,
        "vendorName": order.vendor_name,
        "vendor": order.vendor_name or str(order.vendor_id),
        "warehouse_id": str(order.warehouse_id) if order.warehouse_id else None,
        "warehouseId": str(order.warehouse_id) if order.warehouse_id else None,
        "warehouse_name": order.warehouse_name,
        "warehouseName": order.warehouse_name,
        "items": item_count,
        "status": order.status,
        "priority": order.priority,
        "subtotal": order.subtotal,
        "tax_amount": order.tax_amount,
        "taxAmount": order.tax_amount,
        "discount": order.discount,
        "total_amount": order.total_amount,
        "totalAmount": order.total_amount,
        "total": order.total_amount,
        "currency": order.currency,
        "notes": order.notes,
        "date": order.created_at,
        "expected_delivery_date": order.expected_delivery_date,
        "expectedDelivery": expected_delivery,
        "delivered_date": order.delivered_date,
        "deliveredDate": order.delivered_date,
        "created_at": order.created_at,
        "updated_at": order.updated_at,
    }


@router.get("/")
async def list_orders(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    search: str = Query(None),
    status_filter: str = Query(None, alias="status"),
    vendor_id: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    skip = (page - 1) * per_page
    params = PaginationParams(page=page, per_page=per_page, sort_by=sort_by, sort_order=sort_order)
    service = OrderService(db)
    items, total = await service.list(params, skip=skip, search=search, status=status_filter, vendor_id=vendor_id)
    total_pages = (total + per_page - 1) // per_page
    meta = PaginationMeta(
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )
    data = [await serialize_order(item, db) for item in items]
    return APIResponse(success=True, message="Orders retrieved successfully", data=data, meta=meta)


@router.get("/status-distribution")
async def get_status_distribution(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    service = OrderService(db)
    data = await service.get_status_distribution()
    return APIResponse(success=True, message="Status distribution retrieved successfully", data=data)


@router.get("/monthly-trends")
async def get_monthly_trends(
    year: int = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    service = OrderService(db)
    data = await service.get_monthly_trends(year=year)
    return APIResponse(success=True, message="Monthly trends retrieved successfully", data=data)


@router.get("/recent/list")
async def get_recent_orders(
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    service = OrderService(db)
    data = await service.get_recent(limit=limit)
    return APIResponse(success=True, message="Recent orders retrieved successfully", data=[await serialize_order(item, db) for item in data])


@router.get("/by-vendor/{vendor_id}")
async def get_orders_by_vendor(
    vendor_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    skip = (page - 1) * per_page
    service = OrderService(db)
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
    data = [await serialize_order(item, db) for item in items]
    return APIResponse(success=True, message="Orders by vendor retrieved successfully", data=data, meta=meta)


@router.get("/{order_id}")
async def get_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    service = OrderService(db)
    data = await service.get_by_id(order_id)
    return APIResponse(success=True, message="Order retrieved successfully", data=await serialize_order(data, db))


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_order(
    body: OrderCreate,
    current_user: User = Depends(require_roles(["admin", "warehouse_manager"])),
    db: AsyncSession = Depends(get_async_session),
):
    service = OrderService(db)
    data = await service.create(body, current_user)
    return APIResponse(success=True, message="Order created successfully", data=await serialize_order(data, db))


@router.api_route("/{order_id}", methods=["PATCH", "PUT"])
async def update_order(
    order_id: str,
    body: OrderUpdate,
    current_user: User = Depends(require_roles(["admin", "warehouse_manager"])),
    db: AsyncSession = Depends(get_async_session),
):
    service = OrderService(db)
    data = await service.update(order_id, body)
    return APIResponse(success=True, message="Order updated successfully", data=await serialize_order(data, db))


@router.delete("/{order_id}")
async def delete_order(
    order_id: str,
    current_user: User = Depends(require_roles(["admin"])),
    db: AsyncSession = Depends(get_async_session),
):
    service = OrderService(db)
    await service.delete(order_id)
    return APIResponse(success=True, message="Order deleted successfully")


@router.api_route("/{order_id}/approve", methods=["PATCH", "PUT"])
async def approve_order(
    order_id: str,
    body: OrderApproval = None,
    current_user: User = Depends(require_roles(["admin", "warehouse_manager"])),
    db: AsyncSession = Depends(get_async_session),
):
    service = OrderService(db)
    data = await service.approve(order_id, body, current_user)
    return APIResponse(success=True, message="Order approval updated successfully", data=await serialize_order(data, db))
