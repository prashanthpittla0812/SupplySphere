from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.common import PaginationMeta
from app.core.security import hash_password
from app.core.exceptions import ConflictException, NotFoundException
from app.services.audit_log import AuditLogService


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.audit_log_service = AuditLogService(db)

    def _uuid(self, value) -> UUID:
        return value if isinstance(value, UUID) else UUID(str(value))

    async def create_user(self, data: UserCreate) -> User:
        existing_email = await self.user_repo.get_by_email(data.email)
        if existing_email:
            raise ConflictException("Email already registered")
        existing_username = await self.user_repo.get_by_username(data.username)
        if existing_username:
            raise ConflictException("Username already taken")

        user = await self.user_repo.create(
            email=data.email,
            username=data.username,
            full_name=data.full_name,
            phone=data.phone,
            hashed_password=hash_password(data.password),
            role=data.role,
            is_active=data.is_active,
        )
        return user

    async def create(self, data: UserCreate) -> User:
        return await self.create_user(data)

    async def update_user(self, user_id: UUID, data: UserUpdate) -> User:
        user_id = self._uuid(user_id)
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")

        update_data = data.model_dump(exclude_unset=True)
        if "email" in update_data and update_data["email"]:
            existing = await self.user_repo.get_by_email(update_data["email"])
            if existing and existing.id != user_id:
                raise ConflictException("Email already in use")
        if "username" in update_data and update_data["username"]:
            existing = await self.user_repo.get_by_username(update_data["username"])
            if existing and existing.id != user_id:
                raise ConflictException("Username already taken")

        user = await self.user_repo.update(user_id, **update_data)
        return user

    async def update(self, user_id: UUID, data: UserUpdate) -> User:
        return await self.update_user(user_id, data)

    async def delete_user(self, user_id: UUID) -> bool:
        user_id = self._uuid(user_id)
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")
        return await self.user_repo.soft_delete(user_id)

    async def delete(self, user_id: UUID) -> bool:
        return await self.delete_user(user_id)

    async def get_user(self, user_id: UUID) -> User:
        user_id = self._uuid(user_id)
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")
        return user

    async def get_by_id(self, user_id: UUID) -> User:
        return await self.get_user(user_id)

    async def list(self, params, skip: int = 0, search: Optional[str] = None, **filters) -> Tuple[List[User], int]:
        filters = {key: value for key, value in filters.items() if value is not None}
        items, total = await self.user_repo.list_all(
            skip=skip,
            limit=params.per_page,
            sort_by=params.sort_by,
            sort_order=params.sort_order,
            filters=filters or None,
            search=search,
            search_fields=["full_name", "email", "username"],
        )
        return items, total

    async def list_users(
        self,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Tuple[List[User], PaginationMeta]:
        filters = {}
        if role:
            filters["role"] = role
        if is_active is not None:
            filters["is_active"] = is_active

        skip = (page - 1) * per_page
        items, total = await self.user_repo.list_all(
            skip=skip,
            limit=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            filters=filters,
            search=search,
            search_fields=["full_name", "email", "username"],
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
        return items, meta

    async def search_users(self, query: str, page: int = 1, per_page: int = 20) -> Tuple[List[User], PaginationMeta]:
        skip = (page - 1) * per_page
        items, total = await self.user_repo.search(query, skip=skip, limit=per_page)
        total_pages = max(1, (total + per_page - 1) // per_page)
        meta = PaginationMeta(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )
        return items, meta
