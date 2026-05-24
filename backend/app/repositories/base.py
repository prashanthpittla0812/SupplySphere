from typing import Optional, TypeVar, Generic, List, Type, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete, update
from sqlalchemy.sql import Select
from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, id: UUID) -> Optional[ModelType]:
        query = select(self.model).where(self.model.id == id, self.model.is_deleted == False)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_id_with_deleted(self, id: UUID) -> Optional[ModelType]:
        query = select(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 20,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
        filters: Optional[Dict[str, Any]] = None,
        search: Optional[str] = None,
        search_fields: Optional[List[str]] = None,
    ) -> tuple[List[ModelType], int]:
        query = select(self.model).where(self.model.is_deleted == False)
        count_query = select(func.count(self.model.id)).where(self.model.is_deleted == False)

        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key) and value is not None:
                    query = query.where(getattr(self.model, key) == value)
                    count_query = count_query.where(getattr(self.model, key) == value)

        if search and search_fields:
            conditions = [getattr(self.model, f).ilike(f"%{search}%") for f in search_fields if hasattr(self.model, f)]
            if conditions:
                from sqlalchemy import or_
                query = query.where(or_(*conditions))
                count_query = count_query.where(or_(*conditions))

        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0

        if sort_by and hasattr(self.model, sort_by):
            sort_col = getattr(self.model, sort_by)
            query = query.order_by(sort_col.desc() if sort_order == "desc" else sort_col.asc())
        else:
            query = query.order_by(self.model.created_at.desc())

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        items = list(result.scalars().all())
        return items, total

    async def create(self, **kwargs) -> ModelType:
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def update(self, id: UUID, **kwargs) -> Optional[ModelType]:
        instance = await self.get_by_id(id)
        if not instance:
            return None
        for key, value in kwargs.items():
            if value is not None and hasattr(instance, key):
                setattr(instance, key, value)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def soft_delete(self, id: UUID) -> bool:
        from datetime import datetime, timezone
        instance = await self.get_by_id(id)
        if not instance:
            return False
        instance.is_deleted = True
        instance.deleted_at = datetime.now(timezone.utc)
        await self.session.flush()
        return True

    async def hard_delete(self, id: UUID) -> bool:
        query = delete(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        return result.rowcount > 0

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        query = select(func.count(self.model.id)).where(self.model.is_deleted == False)
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key) and value is not None:
                    query = query.where(getattr(self.model, key) == value)
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def exists(self, **kwargs) -> bool:
        conditions = [getattr(self.model, k) == v for k, v in kwargs.items() if hasattr(self.model, k)]
        query = select(self.model).where(*conditions, self.model.is_deleted == False)
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None
