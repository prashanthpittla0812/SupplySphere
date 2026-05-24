from typing import Optional, List, Tuple
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update

from app.repositories.base import BaseRepository
from app.models.notification import Notification


class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, session: AsyncSession):
        super().__init__(Notification, session)

    async def get_by_user(
        self, user_id: UUID, skip: int = 0, limit: int = 20, unread_only: bool = False
    ) -> Tuple[List[Notification], int]:
        conditions = [Notification.user_id == user_id]
        if unread_only:
            conditions.append(Notification.is_read == False)

        q = select(Notification).where(*conditions).offset(skip).limit(limit).order_by(Notification.created_at.desc())
        count_q = select(func.count(Notification.id)).where(*conditions)
        result = await self.session.execute(q)
        items = list(result.scalars().all())
        total_result = await self.session.execute(count_q)
        total = total_result.scalar() or 0
        return items, total

    async def get_unread_count(self, user_id: UUID) -> int:
        query = select(func.count(Notification.id)).where(
            Notification.user_id == user_id, Notification.is_read == False
        )
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def mark_as_read(self, notification_id: UUID) -> bool:
        notif = await self.get_by_id(notification_id)
        if not notif:
            return False
        notif.is_read = True
        notif.read_at = datetime.now(timezone.utc)
        await self.session.flush()
        return True

    async def mark_all_as_read(self, user_id: UUID) -> int:
        stmt = (
            update(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.is_read == False,
            )
            .values(is_read=True, read_at=datetime.now(timezone.utc))
        )
        result = await self.session.execute(stmt)
        return result.rowcount

    async def create_bulk(self, notifications_data: List[dict]) -> List[Notification]:
        instances = [Notification(**data) for data in notifications_data]
        self.session.add_all(instances)
        await self.session.flush()
        for inst in instances:
            await self.session.refresh(inst)
        return instances
