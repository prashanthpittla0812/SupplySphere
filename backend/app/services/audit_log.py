from datetime import datetime
from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.audit_log import AuditLog
from app.schemas.common import PaginationMeta


class AuditLogRepository:
    def __init__(self, session: AsyncSession):
        from app.repositories.base import BaseRepository
        self._repo = BaseRepository(AuditLog, session)
        self.session = session

    async def create(self, **kwargs) -> AuditLog:
        return await self._repo.create(**kwargs)

    async def list_all(self, **kwargs) -> Tuple[List[AuditLog], int]:
        return await self._repo.list_all(**kwargs)


class AuditLogService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.audit_log_repo = AuditLogRepository(db)

    async def log_action(
        self,
        user_id: Optional[UUID],
        action: str,
        entity_type: str,
        entity_id: Optional[UUID] = None,
        changes: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        description: Optional[str] = None,
    ) -> AuditLog:
        log = await self.audit_log_repo.create(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent,
            description=description,
        )
        return log

    async def list_logs(
        self,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        action: Optional[str] = None,
        entity_type: Optional[str] = None,
        user_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Tuple[List[AuditLog], PaginationMeta]:
        filters = {}
        if action:
            filters["action"] = action
        if entity_type:
            filters["entity_type"] = entity_type
        if user_id:
            filters["user_id"] = user_id
        if start_date:
            filters["created_at__gte"] = start_date
        if end_date:
            filters["created_at__lte"] = end_date

        skip = (page - 1) * per_page
        items, total = await self.audit_log_repo.list_all(
            skip=skip,
            limit=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            filters=filters if filters else None,
            search=search,
            search_fields=["action", "entity_type", "description"],
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

    async def list(self, params, skip: int = 0, search: Optional[str] = None, **filters) -> Tuple[List[AuditLog], int]:
        filters = {key: value for key, value in filters.items() if value is not None}
        return await self.audit_log_repo.list_all(
            skip=skip,
            limit=params.per_page,
            sort_by=params.sort_by,
            sort_order=params.sort_order,
            filters=filters or None,
            search=search,
            search_fields=["action", "entity_type", "description"],
        )
