from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_session
from app.core.dependencies import get_current_user, require_roles
from app.models.user import User
from app.schemas.common import APIResponse, PaginationParams, PaginationMeta
from app.schemas.shipment import ShipmentCreate, ShipmentUpdate, TrackingUpdate
from app.services.shipment import ShipmentService

router = APIRouter(prefix="/shipments", tags=["Shipments"])


def serialize_shipment(shipment):
    status = shipment.status.value if hasattr(shipment.status, "value") else shipment.status
    origin = shipment.warehouse_name or shipment.current_location or "Warehouse"
    destination = shipment.destination_address or "Destination"
    estimated_delivery = shipment.estimated_delivery or shipment.actual_delivery or shipment.created_at
    return {
        "id": str(shipment.id),
        "tracking_number": shipment.tracking_number,
        "trackingNumber": shipment.tracking_number,
        "order_id": str(shipment.order_id),
        "orderId": shipment.order_number or str(shipment.order_id),
        "order_number": shipment.order_number,
        "orderNumber": shipment.order_number,
        "carrier": shipment.carrier,
        "status": status,
        "origin_warehouse_id": str(shipment.origin_warehouse_id) if shipment.origin_warehouse_id else None,
        "originWarehouseId": str(shipment.origin_warehouse_id) if shipment.origin_warehouse_id else None,
        "warehouse_name": shipment.warehouse_name,
        "warehouseName": shipment.warehouse_name,
        "origin": origin,
        "destination_address": shipment.destination_address,
        "destinationAddress": shipment.destination_address,
        "destination": destination,
        "estimated_delivery": shipment.estimated_delivery,
        "estimatedDelivery": estimated_delivery,
        "actual_delivery": shipment.actual_delivery,
        "actualDelivery": shipment.actual_delivery,
        "shipped_date": shipment.shipped_date,
        "shippedDate": shipment.shipped_date,
        "current_location": shipment.current_location,
        "currentLocation": shipment.current_location,
        "last_updated": shipment.last_updated,
        "lastUpdated": shipment.last_updated,
        "created_at": shipment.created_at,
        "updated_at": shipment.updated_at,
    }


@router.get("/")
async def list_shipments(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    search: str = Query(None),
    status_filter: str = Query(None, alias="status"),
    order_id: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    skip = (page - 1) * per_page
    params = PaginationParams(page=page, per_page=per_page, sort_by=sort_by, sort_order=sort_order)
    service = ShipmentService(db)
    items, total = await service.list(params, skip=skip, search=search, status=status_filter, order_id=order_id)
    total_pages = (total + per_page - 1) // per_page
    meta = PaginationMeta(
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )
    return APIResponse(success=True, message="Shipments retrieved successfully", data=[serialize_shipment(item) for item in items], meta=meta)


@router.get("/by-order/{order_id}")
async def get_shipments_by_order(
    order_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    skip = (page - 1) * per_page
    service = ShipmentService(db)
    items, total = await service.get_by_order(order_id, skip=skip, per_page=per_page)
    total_pages = (total + per_page - 1) // per_page
    meta = PaginationMeta(
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )
    return APIResponse(success=True, message="Shipments by order retrieved successfully", data=[serialize_shipment(item) for item in items], meta=meta)


@router.get("/{shipment_id}")
async def get_shipment(
    shipment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    service = ShipmentService(db)
    data = await service.get_by_id(shipment_id)
    return APIResponse(success=True, message="Shipment retrieved successfully", data=serialize_shipment(data))


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_shipment(
    body: ShipmentCreate,
    current_user: User = Depends(require_roles(["admin", "warehouse_manager"])),
    db: AsyncSession = Depends(get_async_session),
):
    service = ShipmentService(db)
    data = await service.create(body)
    return APIResponse(success=True, message="Shipment created successfully", data=serialize_shipment(data))


@router.api_route("/{shipment_id}", methods=["PATCH", "PUT"])
async def update_shipment(
    shipment_id: str,
    body: ShipmentUpdate,
    current_user: User = Depends(require_roles(["admin", "warehouse_manager"])),
    db: AsyncSession = Depends(get_async_session),
):
    service = ShipmentService(db)
    data = await service.update(shipment_id, body)
    return APIResponse(success=True, message="Shipment updated successfully", data=serialize_shipment(data))


@router.delete("/{shipment_id}")
async def delete_shipment(
    shipment_id: str,
    current_user: User = Depends(require_roles(["admin"])),
    db: AsyncSession = Depends(get_async_session),
):
    service = ShipmentService(db)
    await service.delete(shipment_id)
    return APIResponse(success=True, message="Shipment deleted successfully")


@router.api_route("/{shipment_id}/track", methods=["PATCH", "PUT"])
async def update_tracking(
    shipment_id: str,
    body: TrackingUpdate,
    current_user: User = Depends(require_roles(["admin", "warehouse_manager", "delivery_personnel"])),
    db: AsyncSession = Depends(get_async_session),
):
    service = ShipmentService(db)
    data = await service.update_tracking(shipment_id, body)
    return APIResponse(success=True, message="Tracking updated successfully", data=serialize_shipment(data))


@router.api_route("/{shipment_id}/tracking", methods=["PATCH", "PUT"])
async def update_tracking_alias(
    shipment_id: str,
    body: TrackingUpdate,
    current_user: User = Depends(require_roles(["admin", "warehouse_manager", "delivery_personnel"])),
    db: AsyncSession = Depends(get_async_session),
):
    return await update_tracking(shipment_id, body, current_user, db)
