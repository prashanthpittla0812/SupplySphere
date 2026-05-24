from typing import Optional, List, Type, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.repositories.base import BaseRepository
from app.models.user import User


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> Optional[User]:
        query = select(User).where(User.email == email, User.is_deleted == False)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        query = select(User).where(User.username == username, User.is_deleted == False)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_active_users_count(self) -> int:
        query = select(func.count(User.id)).where(User.is_active == True, User.is_deleted == False)
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def get_by_role(self, role: str) -> List[User]:
        query = select(User).where(User.role == role, User.is_deleted == False)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def search(
        self, query: str, skip: int = 0, limit: int = 20
    ) -> Tuple[List[User], int]:
        search_filter = or_(
            User.full_name.ilike(f"%{query}%"),
            User.email.ilike(f"%{query}%"),
            User.username.ilike(f"%{query}%"),
        )
        q = select(User).where(search_filter, User.is_deleted == False).offset(skip).limit(limit).order_by(User.created_at.desc())
        count_q = select(func.count(User.id)).where(search_filter, User.is_deleted == False)
        result = await self.session.execute(q)
        items = list(result.scalars().all())
        total_result = await self.session.execute(count_q)
        total = total_result.scalar() or 0
        return items, total
