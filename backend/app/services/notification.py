from datetime import datetime, timezone
from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update

from app.models.notification import Notification
from app.schemas.common import PaginationMeta
from app.core.exceptions import NotFoundException


class NotificationRepository:
    def __init__(self, session: AsyncSession):
        from app.repositories.base import BaseRepository
        self._repo = BaseRepository(Notification, session)
        self.session = session

    async def get_by_id(self, id: UUID) -> Optional[Notification]:
        id = id if isinstance(id, UUID) else UUID(str(id))
        return await self._repo.get_by_id(id)

    async def create(self, **kwargs) -> Notification:
        return await self._repo.create(**kwargs)

    async def list_all(self, **kwargs) -> Tuple[List[Notification], int]:
        return await self._repo.list_all(**kwargs)

    async def get_user_notifications(
        self, user_id: UUID, skip: int = 0, limit: int = 20, unread_only: bool = False
    ) -> Tuple[List[Notification], int, int]:
        conditions = [Notification.user_id == user_id]
        if unread_only:
            conditions.append(Notification.is_read == False)

        query = select(Notification).where(*conditions).order_by(Notification.created_at.desc()).offset(skip).limit(limit)
        count_q = select(func.count(Notification.id)).where(*conditions)
        unread_q = select(func.count(Notification.id)).where(
            Notification.user_id == user_id, Notification.is_read == False
        )

        result = await self.session.execute(query)
        items = list(result.scalars().all())

        total_result = await self.session.execute(count_q)
        total = total_result.scalar() or 0

        unread_result = await self.session.execute(unread_q)
        unread_count = unread_result.scalar() or 0

        return items, total, unread_count

    async def mark_as_read(self, notification_id: UUID, user_id: UUID) -> bool:
        notification_id = notification_id if isinstance(notification_id, UUID) else UUID(str(notification_id))
        query = (
            update(Notification)
            .where(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            )
            .values(is_read=True, read_at=datetime.now(timezone.utc))
        )
        result = await self.session.execute(query)
        await self.session.flush()
        return result.rowcount > 0

    async def mark_all_as_read(self, user_id: UUID) -> int:
        query = (
            update(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.is_read == False,
            )
            .values(is_read=True, read_at=datetime.now(timezone.utc))
        )
        result = await self.session.execute(query)
        await self.session.flush()
        return result.rowcount

    async def get_unread_count(self, user_id: UUID) -> int:
        query = select(func.count(Notification.id)).where(
            Notification.user_id == user_id,
            Notification.is_read == False,
        )
        result = await self.session.execute(query)
        return result.scalar() or 0


class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.notification_repo = NotificationRepository(db)

    async def create_notification(self, data) -> Notification:
        notification = await self.notification_repo.create(
            user_id=data.user_id,
            title=data.title,
            message=data.message,
            type=getattr(data, 'type', 'info'),
            category=getattr(data, 'category', 'system'),
            reference_type=getattr(data, 'reference_type', None),
            reference_id=getattr(data, 'reference_id', None),
            action_url=getattr(data, 'action_url', None),
        )
        return notification

    async def get_user_notifications(
        self, user_id: UUID, page: int = 1, per_page: int = 20, unread_only: bool = False
    ) -> Tuple[List[Notification], PaginationMeta, int]:
        skip = (page - 1) * per_page
        items, total, unread_count = await self.notification_repo.get_user_notifications(
            user_id, skip=skip, limit=per_page, unread_only=unread_only
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
        return items, meta, unread_count

    async def mark_as_read(self, notification_id: UUID, user_id: UUID) -> bool:
        notification_id = notification_id if isinstance(notification_id, UUID) else UUID(str(notification_id))
        result = await self.notification_repo.mark_as_read(notification_id, user_id)
        if not result:
            raise NotFoundException("Notification not found")
        return True

    async def mark_all_as_read(self, user_id: UUID) -> int:
        return await self.notification_repo.mark_all_as_read(user_id)

    async def send_bulk_notification(self, notification_data, user_ids: List[UUID]) -> List[Notification]:
        notifications = []
        for user_id in user_ids:
            notification = await self.notification_repo.create(
                user_id=user_id,
                title=notification_data.title,
                message=notification_data.message,
                type=getattr(notification_data, 'type', 'info'),
                category=getattr(notification_data, 'category', 'system'),
                reference_type=getattr(notification_data, 'reference_type', None),
                reference_id=getattr(notification_data, 'reference_id', None),
                action_url=getattr(notification_data, 'action_url', None),
            )
            notifications.append(notification)
        return notifications

    async def get_unread_count(self, user_id: UUID) -> int:
        return await self.notification_repo.get_unread_count(user_id)
