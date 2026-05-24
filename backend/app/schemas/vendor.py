import re
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


def validate_gst(v: Optional[str]) -> Optional[str]:
    if v is not None and v.strip():
        pattern = r"^\d{2}[A-Z]{5}\d{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"
        if not re.match(pattern, v):
            raise ValueError("Invalid GST number format")
    return v


def validate_pan(v: Optional[str]) -> Optional[str]:
    if v is not None and v.strip():
        pattern = r"^[A-Z]{5}\d{4}[A-Z]{1}$"
        if not re.match(pattern, v):
            raise ValueError("Invalid PAN number format")
    return v


class VendorBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    company_name: str = Field(..., min_length=1, max_length=200)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=20)
    address: str = Field(..., min_length=1, max_length=500)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=100)
    country: str = Field(..., min_length=1, max_length=100)
    pincode: str = Field(..., min_length=1, max_length=20)
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    contact_person: Optional[str] = Field(default=None, max_length=200)

    @field_validator("gst_number")
    @classmethod
    def check_gst(cls, v: Optional[str]) -> Optional[str]:
        return validate_gst(v)

    @field_validator("pan_number")
    @classmethod
    def check_pan(cls, v: Optional[str]) -> Optional[str]:
        return validate_pan(v)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.match(r"^\+?[0-9][0-9\-\s()]{7,19}$", v):
            raise ValueError("Phone number must be valid")
        return v


class VendorCreate(VendorBase):
    notes: Optional[str] = Field(default=None, max_length=1000)


class VendorUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    company_name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, min_length=10, max_length=20)
    address: Optional[str] = Field(default=None, min_length=1, max_length=500)
    city: Optional[str] = Field(default=None, min_length=1, max_length=100)
    state: Optional[str] = Field(default=None, min_length=1, max_length=100)
    country: Optional[str] = Field(default=None, min_length=1, max_length=100)
    pincode: Optional[str] = Field(default=None, min_length=1, max_length=20)
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    contact_person: Optional[str] = Field(default=None, max_length=200)
    status: Optional[str] = Field(default=None, pattern=r"^(active|inactive|blacklisted)$")
    notes: Optional[str] = Field(default=None, max_length=1000)

    @field_validator("gst_number")
    @classmethod
    def check_gst(cls, v: Optional[str]) -> Optional[str]:
        return validate_gst(v)

    @field_validator("pan_number")
    @classmethod
    def check_pan(cls, v: Optional[str]) -> Optional[str]:
        return validate_pan(v)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip():
            if not re.match(r"^\+?[0-9][0-9\-\s()]{7,19}$", v):
                raise ValueError("Phone number must be valid")
        return v


class VendorOut(BaseModel):
    id: UUID
    name: str
    company_name: str
    email: str
    phone: str
    address: str
    city: str
    state: str
    country: str
    pincode: str
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    contact_person: Optional[str] = None
    status: str
    rating: Optional[float] = None
    total_orders: int = 0
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None

    model_config = {"from_attributes": True}
