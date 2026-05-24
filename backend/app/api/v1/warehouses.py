from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_session
from app.core.dependencies import get_current_user, require_roles
from app.models.user import User
from app.schemas.common import APIResponse, PaginationParams, PaginationMeta
from app.schemas.warehouse import WarehouseCreate, WarehouseUpdate
from app.services.warehouse import WarehouseService

router = APIRouter(prefix="/warehouses", tags=["Warehouses"])


def serialize_warehouse(warehouse):
    location = ", ".join(part for part in [warehouse.city, warehouse.state, warehouse.country] if part)
    status = "operational" if warehouse.status == "active" else warehouse.status
    return {
        "id": str(warehouse.id),
        "name": warehouse.name,
        "code": warehouse.code,
        "address": warehouse.address,
        "city": warehouse.city,
        "state": warehouse.state,
        "country": warehouse.country,
        "pincode": warehouse.pincode,
        "location": location,
        "capacity": warehouse.capacity,
        "used_capacity": warehouse.used_capacity,
        "usedCapacity": warehouse.used_capacity,
        "currentStock": warehouse.used_capacity,
        "status": status,
        "manager_id": str(warehouse.manager_id) if warehouse.manager_id else None,
        "managerId": str(warehouse.manager_id) if warehouse.manager_id else None,
        "manager_name": warehouse.manager_name,
        "managerName": warehouse.manager_name,
        "latitude": warehouse.latitude,
        "longitude": warehouse.longitude,
        "created_at": warehouse.created_at,
        "updated_at": warehouse.updated_at,
    }


@router.get("/")
async def list_warehouses(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    search: str = Query(None),
    status_filter: str = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    skip = (page - 1) * per_page
    params = PaginationParams(page=page, per_page=per_page, sort_by=sort_by, sort_order=sort_order)
    service = WarehouseService(db)
    items, total = await service.list(params, skip=skip, search=search, status=status_filter)
    total_pages = (total + per_page - 1) // per_page
    meta = PaginationMeta(
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )
    return APIResponse(success=True, message="Warehouses retrieved successfully", data=[serialize_warehouse(item) for item in items], meta=meta)


@router.get("/available/list")
async def get_available_warehouses(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    skip = (page - 1) * per_page
    service = WarehouseService(db)
    items, total = await service.get_available(skip=skip, per_page=per_page)
    total_pages = (total + per_page - 1) // per_page
    meta = PaginationMeta(
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )
    return APIResponse(success=True, message="Available warehouses retrieved successfully", data=[serialize_warehouse(item) for item in items], meta=meta)


@router.get("/{warehouse_id}")
async def get_warehouse(
    warehouse_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    service = WarehouseService(db)
    data = await service.get_by_id(warehouse_id)
    return APIResponse(success=True, message="Warehouse retrieved successfully", data=serialize_warehouse(data))


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_warehouse(
    body: WarehouseCreate,
    current_user: User = Depends(require_roles(["admin"])),
    db: AsyncSession = Depends(get_async_session),
):
    service = WarehouseService(db)
    data = await service.create(body)
    return APIResponse(success=True, message="Warehouse created successfully", data=serialize_warehouse(data))


@router.api_route("/{warehouse_id}", methods=["PATCH", "PUT"])
async def update_warehouse(
    warehouse_id: str,
    body: WarehouseUpdate,
    current_user: User = Depends(require_roles(["admin"])),
    db: AsyncSession = Depends(get_async_session),
):
    service = WarehouseService(db)
    data = await service.update(warehouse_id, body)
    return APIResponse(success=True, message="Warehouse updated successfully", data=serialize_warehouse(data))


@router.delete("/{warehouse_id}")
async def delete_warehouse(
    warehouse_id: str,
    current_user: User = Depends(require_roles(["admin"])),
    db: AsyncSession = Depends(get_async_session),
):
    service = WarehouseService(db)
    await service.delete(warehouse_id)
    return APIResponse(success=True, message="Warehouse deleted successfully")
