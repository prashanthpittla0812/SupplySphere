from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Optional, List
from datetime import datetime
from uuid import UUID

T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)
    sort_by: Optional[str] = None
    sort_order: Optional[str] = "desc"


class PaginationMeta(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool


class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Success"
    data: Optional[T] = None
    meta: Optional[PaginationMeta] = None


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    data: Optional[dict] = None
