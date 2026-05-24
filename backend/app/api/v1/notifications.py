from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_session
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.common import APIResponse, PaginationParams, PaginationMeta
from app.services.notification import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])


def serialize_notification(notification):
    notification_type = notification.type.value if hasattr(notification.type, "value") else notification.type
    category = notification.category.value if hasattr(notification.category, "value") else notification.category
    return {
        "id": str(notification.id),
        "title": notification.title,
        "message": notification.message,
        "type": notification_type,
        "category": category,
        "reference_type": notification.reference_type,
        "referenceType": notification.reference_type,
        "reference_id": str(notification.reference_id) if notification.reference_id else None,
        "referenceId": str(notification.reference_id) if notification.reference_id else None,
        "is_read": notification.is_read,
        "isRead": notification.is_read,
        "read_at": notification.read_at,
        "readAt": notification.read_at,
        "action_url": notification.action_url,
        "actionUrl": notification.action_url,
        "created_at": notification.created_at,
        "createdAt": notification.created_at,
    }


@router.get("/")
async def list_notifications(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    skip = (page - 1) * per_page
    service = NotificationService(db)
    items, meta, unread_count = await service.get_user_notifications(current_user.id, page=page, per_page=per_page)
    total = meta.total
    total_pages = (total + per_page - 1) // per_page
    meta = PaginationMeta(
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )
    return APIResponse(success=True, message="Notifications retrieved successfully", data=[serialize_notification(item) for item in items], meta=meta)


@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    service = NotificationService(db)
    data = await service.get_unread_count(current_user.id)
    return APIResponse(success=True, message="Unread count retrieved successfully", data=data)


@router.patch("/{notification_id}/read")
async def mark_as_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    service = NotificationService(db)
    data = await service.mark_as_read(notification_id, current_user.id)
    return APIResponse(success=True, message="Notification marked as read", data=data)


@router.patch("/read-all")
async def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    service = NotificationService(db)
    data = await service.mark_all_as_read(current_user.id)
    return APIResponse(success=True, message="All notifications marked as read", data=data)
