from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_session
from app.core.dependencies import get_current_user, require_roles
from app.models.user import User
from app.schemas.common import APIResponse, PaginationParams, PaginationMeta
from app.schemas.user import UserCreate, UserUpdate
from app.services.user import UserService

router = APIRouter(prefix="/users", tags=["Users"])


def serialize_user(user):
    role = user.role.value if hasattr(user.role, "value") else user.role
    status = "active" if user.is_active else "inactive"
    last_login = user.updated_at or user.created_at
    return {
        "id": str(user.id),
        "name": user.full_name,
        "full_name": user.full_name,
        "fullName": user.full_name,
        "email": user.email,
        "username": user.username,
        "phone": user.phone,
        "role": role,
        "status": status,
        "is_active": user.is_active,
        "isActive": user.is_active,
        "is_verified": user.is_verified,
        "isVerified": user.is_verified,
        "lastLogin": last_login,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }


@router.get("/")
async def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    search: str = Query(None),
    current_user: User = Depends(require_roles(["admin", "warehouse_manager"])),
    db: AsyncSession = Depends(get_async_session),
):
    skip = (page - 1) * per_page
    params = PaginationParams(page=page, per_page=per_page, sort_by=sort_by, sort_order=sort_order)
    service = UserService(db)
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
    return APIResponse(success=True, message="Users retrieved successfully", data=[serialize_user(item) for item in items], meta=meta)


@router.get("/{user_id}")
async def get_user(
    user_id: str,
    current_user: User = Depends(require_roles(["admin"])),
    db: AsyncSession = Depends(get_async_session),
):
    service = UserService(db)
    data = await service.get_by_id(user_id)
    return APIResponse(success=True, message="User retrieved successfully", data=serialize_user(data))


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    body: UserCreate,
    current_user: User = Depends(require_roles(["admin"])),
    db: AsyncSession = Depends(get_async_session),
):
    service = UserService(db)
    data = await service.create(body)
    return APIResponse(success=True, message="User created successfully", data=serialize_user(data))


@router.api_route("/{user_id}", methods=["PATCH", "PUT"])
async def update_user(
    user_id: str,
    body: UserUpdate,
    current_user: User = Depends(require_roles(["admin"])),
    db: AsyncSession = Depends(get_async_session),
):
    service = UserService(db)
    data = await service.update(user_id, body)
    return APIResponse(success=True, message="User updated successfully", data=serialize_user(data))


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(require_roles(["admin"])),
    db: AsyncSession = Depends(get_async_session),
):
    service = UserService(db)
    await service.delete(user_id)
    return APIResponse(success=True, message="User deleted successfully")
