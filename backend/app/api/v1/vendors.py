from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_session
from app.core.dependencies import get_current_user, require_roles
from app.models.user import User
from app.schemas.common import APIResponse, PaginationParams, PaginationMeta
from app.schemas.vendor import VendorCreate, VendorUpdate
from app.services.vendor import VendorService

router = APIRouter(prefix="/vendors", tags=["Vendors"])


def serialize_vendor(vendor):
    return {
        "id": str(vendor.id),
        "name": vendor.name,
        "company_name": vendor.company_name,
        "companyName": vendor.company_name,
        "email": vendor.email,
        "phone": vendor.phone,
        "address": vendor.address,
        "city": vendor.city,
        "state": vendor.state,
        "country": vendor.country,
        "pincode": vendor.pincode,
        "gst_number": vendor.gst_number,
        "gstNumber": vendor.gst_number,
        "pan_number": vendor.pan_number,
        "panNumber": vendor.pan_number,
        "contact_person": vendor.contact_person,
        "contactPerson": vendor.contact_person,
        "status": vendor.status,
        "rating": vendor.rating or 0,
        "total_orders": vendor.total_orders,
        "totalOrders": vendor.total_orders,
        "notes": vendor.notes,
        "created_by": str(vendor.created_by) if vendor.created_by else None,
        "created_at": vendor.created_at,
        "updated_at": vendor.updated_at,
    }


@router.get("/")
async def list_vendors(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    search: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    skip = (page - 1) * per_page
    params = PaginationParams(page=page, per_page=per_page, sort_by=sort_by, sort_order=sort_order)
    service = VendorService(db)
    items, total = await service.list(params, skip=skip, search=search)
    total_pages = (total + per_page - 1) // per_page
    meta = PaginationMeta(
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )
    return APIResponse(success=True, message="Vendors retrieved successfully", data=[serialize_vendor(item) for item in items], meta=meta)


@router.get("/{vendor_id}")
async def get_vendor(
    vendor_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    service = VendorService(db)
    data = await service.get_by_id(vendor_id)
    return APIResponse(success=True, message="Vendor retrieved successfully", data=serialize_vendor(data))


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_vendor(
    body: VendorCreate,
    current_user: User = Depends(require_roles(["admin", "warehouse_manager"])),
    db: AsyncSession = Depends(get_async_session),
):
    service = VendorService(db)
    data = await service.create(body, current_user)
    return APIResponse(success=True, message="Vendor created successfully", data=serialize_vendor(data))


@router.api_route("/{vendor_id}", methods=["PATCH", "PUT"])
async def update_vendor(
    vendor_id: str,
    body: VendorUpdate,
    current_user: User = Depends(require_roles(["admin", "warehouse_manager"])),
    db: AsyncSession = Depends(get_async_session),
):
    service = VendorService(db)
    data = await service.update(vendor_id, body)
    return APIResponse(success=True, message="Vendor updated successfully", data=serialize_vendor(data))


@router.delete("/{vendor_id}")
async def delete_vendor(
    vendor_id: str,
    current_user: User = Depends(require_roles(["admin"])),
    db: AsyncSession = Depends(get_async_session),
):
    service = VendorService(db)
    await service.delete(vendor_id)
    return APIResponse(success=True, message="Vendor deleted successfully")


@router.api_route("/{vendor_id}/approve", methods=["PATCH", "PUT"])
async def approve_vendor(
    vendor_id: str,
    current_user: User = Depends(require_roles(["admin"])),
    db: AsyncSession = Depends(get_async_session),
):
    service = VendorService(db)
    data = await service.approve(vendor_id)
    return APIResponse(success=True, message="Vendor approved successfully", data=serialize_vendor(data))


@router.api_route("/{vendor_id}/reject", methods=["PATCH", "PUT"])
async def reject_vendor(
    vendor_id: str,
    current_user: User = Depends(require_roles(["admin"])),
    db: AsyncSession = Depends(get_async_session),
):
    service = VendorService(db)
    data = await service.reject(vendor_id)
    return APIResponse(success=True, message="Vendor rejected successfully", data=serialize_vendor(data))
