from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ShipmentCreate(BaseModel):
    order_id: UUID
    carrier: str = Field(..., min_length=1, max_length=100)
    origin_warehouse_id: Optional[UUID] = None
    destination_address: Optional[str] = Field(default=None, max_length=500)
    estimated_delivery: Optional[date] = None
    weight: Optional[float] = Field(default=None, ge=0)
    dimensions: Optional[str] = Field(default=None, max_length=100)
    notes: Optional[str] = Field(default=None, max_length=1000)
    tracking_number: Optional[str] = Field(default=None, max_length=100)


class ShipmentUpdate(BaseModel):
    carrier: Optional[str] = Field(default=None, min_length=1, max_length=100)
    status: Optional[str] = Field(
        default=None,
        pattern=r"^(pending|picked_up|in_transit|out_for_delivery|delivered|failed|cancelled)$",
    )
    current_location: Optional[str] = Field(default=None, max_length=500)
    estimated_delivery: Optional[date] = None
    notes: Optional[str] = Field(default=None, max_length=1000)
    tracking_number: Optional[str] = Field(default=None, max_length=100)


class TrackingUpdate(BaseModel):
    model_config = {"populate_by_name": True}

    location: Optional[str] = Field(default=None, alias="current_location", min_length=1, max_length=500)
    status: str = Field(..., pattern=r"^(pending|picked_up|in_transit|out_for_delivery|delivered|failed|cancelled)$")
    notes: Optional[str] = Field(default=None, max_length=1000)


class ShipmentOut(BaseModel):
    id: UUID
    tracking_number: str
    order_id: UUID
    order_number: str
    carrier: str
    status: str
    origin_warehouse_id: Optional[UUID] = None
    warehouse_name: Optional[str] = None
    destination_address: Optional[str] = None
    estimated_delivery: Optional[date] = None
    actual_delivery: Optional[datetime] = None
    shipped_date: Optional[datetime] = None
    shipped_by: Optional[UUID] = None
    shipped_by_name: Optional[str] = None
    weight: Optional[float] = None
    dimensions: Optional[str] = None
    notes: Optional[str] = None
    current_location: Optional[str] = None
    last_updated: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
