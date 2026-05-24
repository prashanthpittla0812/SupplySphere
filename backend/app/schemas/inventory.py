from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class InventoryBase(BaseModel):
    quantity: float = Field(..., ge=0)
    reserved_quantity: float = Field(default=0, ge=0)
    batch_number: Optional[str] = Field(default=None, max_length=100)
    expiry_date: Optional[date] = None


class InventoryCreate(BaseModel):
    product_id: UUID
    warehouse_id: UUID
    quantity: float = Field(..., ge=0)
    batch_number: Optional[str] = Field(default=None, max_length=100)
    expiry_date: Optional[date] = None


class InventoryUpdate(BaseModel):
    quantity: Optional[float] = Field(default=None, ge=0)
    reserved_quantity: Optional[float] = Field(default=None, ge=0)
    batch_number: Optional[str] = Field(default=None, max_length=100)
    expiry_date: Optional[date] = None
    last_count_date: Optional[datetime] = None


class InventoryOut(BaseModel):
    id: UUID
    product_id: UUID
    product_name: str
    product_sku: str
    warehouse_id: UUID
    warehouse_name: str
    quantity: float
    reserved_quantity: float
    available_quantity: float
    batch_number: Optional[str] = None
    expiry_date: Optional[date] = None
    last_count_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LowStockAlert(BaseModel):
    product_id: UUID
    product_name: str
    current_stock: float
    min_stock_level: float


class StockAdjustRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    adjustment_type: str = Field(default="set", alias="type", pattern=r"^(add|subtract|remove|set)$")
    quantity: float = Field(..., ge=0)
    reason: str = Field(default="Manual stock adjustment", min_length=1, max_length=500)
