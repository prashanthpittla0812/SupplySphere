import re
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class OrderItemCreate(BaseModel):
    product_id: UUID
    quantity: float = Field(..., ge=0.001)
    unit_price: Optional[float] = Field(default=None, ge=0)


class OrderItemOut(BaseModel):
    id: UUID
    product_id: UUID
    product_name: str
    product_sku: str
    quantity: float
    unit_price: float
    total_price: float
    received_quantity: float = 0
    status: str

    model_config = {"from_attributes": True}


class OrderCreate(BaseModel):
    vendor_id: UUID
    warehouse_id: UUID
    items: list[OrderItemCreate] = Field(default_factory=list)
    priority: str = Field(default="medium", pattern=r"^(low|medium|high|critical)$")
    notes: Optional[str] = Field(default=None, max_length=2000)
    terms: Optional[str] = Field(default=None, max_length=2000)
    expected_delivery_date: Optional[date] = None
    is_urgent: bool = False
    discount: Optional[float] = Field(default=0, ge=0)
    currency: str = Field(default="INR", min_length=3, max_length=3)


class OrderUpdate(BaseModel):
    status: Optional[str] = Field(
        default=None,
        pattern=r"^(draft|pending|approved|rejected|processing|shipped|delivered|cancelled)$",
    )
    priority: Optional[str] = Field(default=None, pattern=r"^(low|medium|high|critical)$")
    notes: Optional[str] = Field(default=None, max_length=2000)
    terms: Optional[str] = Field(default=None, max_length=2000)
    expected_delivery_date: Optional[date] = None
    is_urgent: Optional[bool] = None
    discount: Optional[float] = Field(default=None, ge=0)


class OrderApproval(BaseModel):
    status: str = Field(..., pattern=r"^(approved|rejected)$")
    notes: Optional[str] = Field(default=None, max_length=2000)


class OrderOut(BaseModel):
    id: UUID
    order_number: str
    vendor_id: UUID
    vendor_name: str
    warehouse_id: UUID
    warehouse_name: str
    status: str
    priority: str
    subtotal: float
    tax_amount: float
    discount: float = 0
    total_amount: float
    currency: str = "INR"
    notes: Optional[str] = None
    terms: Optional[str] = None
    ordered_by: UUID
    ordered_by_name: str
    approved_by: Optional[UUID] = None
    approved_by_name: Optional[str] = None
    approved_at: Optional[datetime] = None
    expected_delivery_date: Optional[date] = None
    delivered_date: Optional[datetime] = None
    is_urgent: bool = False
    items: list[OrderItemOut] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
