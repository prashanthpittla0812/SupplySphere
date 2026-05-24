import re
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


def validate_gst(v: Optional[str]) -> Optional[str]:
    if v is not None and v.strip():
        pattern = r"^\d{2}[A-Z]{5}\d{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"
        if not re.match(pattern, v):
            raise ValueError("Invalid GST number format")
    return v


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    sku: str = Field(..., min_length=1, max_length=50)
    category: str = Field(..., min_length=1, max_length=100)
    unit_price: float = Field(..., ge=0)
    unit_cost: float = Field(..., ge=0)
    tax_rate: float = Field(default=0, ge=0, le=100)
    unit: str = Field(..., min_length=1, max_length=50)
    min_stock_level: float = Field(default=0, ge=0)
    description: Optional[str] = Field(default=None, max_length=2000)
    image_url: Optional[str] = Field(default=None, max_length=500)
    hsn_code: Optional[str] = Field(default=None, max_length=20)
    gst_rate: Optional[float] = Field(default=None, ge=0, le=100)

    @field_validator("sku")
    @classmethod
    def validate_sku(cls, v: str) -> str:
        if not re.match(r"^[A-Za-z0-9\-_]+$", v):
            raise ValueError("SKU must contain only alphanumeric characters, hyphens, and underscores")
        return v


class ProductCreate(ProductBase):
    vendor_id: UUID


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    sku: Optional[str] = Field(default=None, min_length=1, max_length=50)
    category: Optional[str] = Field(default=None, min_length=1, max_length=100)
    unit_price: Optional[float] = Field(default=None, ge=0)
    unit_cost: Optional[float] = Field(default=None, ge=0)
    tax_rate: Optional[float] = Field(default=None, ge=0, le=100)
    unit: Optional[str] = Field(default=None, min_length=1, max_length=50)
    min_stock_level: Optional[float] = Field(default=None, ge=0)
    description: Optional[str] = Field(default=None, max_length=2000)
    image_url: Optional[str] = Field(default=None, max_length=500)
    is_active: Optional[bool] = None
    vendor_id: Optional[UUID] = None
    hsn_code: Optional[str] = Field(default=None, max_length=20)
    gst_rate: Optional[float] = Field(default=None, ge=0, le=100)

    @field_validator("sku")
    @classmethod
    def validate_sku(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not re.match(r"^[A-Za-z0-9\-_]+$", v):
                raise ValueError("SKU must contain only alphanumeric characters, hyphens, and underscores")
        return v


class ProductOut(BaseModel):
    id: UUID
    name: str
    sku: str
    description: Optional[str] = None
    category: str
    unit_price: float
    unit_cost: float
    tax_rate: float
    unit: str
    min_stock_level: float
    image_url: Optional[str] = None
    is_active: bool
    vendor_id: UUID
    vendor_name: str
    hsn_code: Optional[str] = None
    gst_rate: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
