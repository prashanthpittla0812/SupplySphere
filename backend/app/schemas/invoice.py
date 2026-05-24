from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class InvoiceCreate(BaseModel):
    order_id: UUID
    vendor_id: Optional[UUID] = None
    issue_date: date = Field(default_factory=date.today)
    due_date: date
    subtotal: Optional[float] = Field(default=None, ge=0)
    tax_amount: Optional[float] = Field(default=None, ge=0)
    total_amount: Optional[float] = Field(default=None, ge=0)
    notes: Optional[str] = Field(default=None, max_length=1000)


class InvoiceUpdate(BaseModel):
    status: Optional[str] = Field(
        default=None,
        pattern=r"^(draft|sent|paid|overdue|cancelled|refunded)$",
    )
    notes: Optional[str] = Field(default=None, max_length=1000)
    payment_method: Optional[str] = Field(default=None, max_length=50)
    payment_reference: Optional[str] = Field(default=None, max_length=200)


class InvoicePayment(BaseModel):
    amount: float = Field(..., gt=0)
    payment_method: str = Field(default="manual", min_length=1, max_length=50)
    payment_reference: Optional[str] = Field(default=None, max_length=200)
    notes: Optional[str] = Field(default=None, max_length=1000)


PaymentRecord = InvoicePayment


class InvoiceOut(BaseModel):
    id: UUID
    invoice_number: str
    order_id: UUID
    order_number: str
    vendor_id: UUID
    vendor_name: str
    status: str
    issue_date: date
    due_date: date
    paid_date: Optional[datetime] = None
    subtotal: float
    tax_amount: float
    discount: float = 0
    total_amount: float
    amount_paid: float = 0
    balance_due: float = 0
    currency: str = "INR"
    notes: Optional[str] = None
    pdf_url: Optional[str] = None
    payment_method: Optional[str] = None
    payment_reference: Optional[str] = None
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
