from math import ceil
from typing import Optional, Any, Dict, List, Tuple
from app.schemas.common import PaginationMeta, PaginationParams

def paginate(total: int, page: int, per_page: int) -> PaginationMeta:
    return PaginationMeta(
        page=page,
        per_page=per_page,
        total=total,
        total_pages=ceil(total / per_page) if per_page > 0 else 0,
        has_next=(page * per_page) < total,
        has_prev=page > 1,
    )

def get_pagination_params(
    page: int = 1,
    per_page: int = 20,
    sort_by: Optional[str] = None,
    sort_order: str = "desc",
) -> PaginationParams:
    return PaginationParams(
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order,
    )

def get_pagination_meta(total: int, params: PaginationParams) -> PaginationMeta:
    return PaginationMeta(
        page=params.page,
        per_page=params.per_page,
        total=total,
        total_pages=ceil(total / params.per_page) if params.per_page > 0 else 0,
        has_next=(params.page * params.per_page) < total,
        has_prev=params.page > 1,
    )
