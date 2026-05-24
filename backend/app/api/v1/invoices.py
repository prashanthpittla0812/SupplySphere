from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_session
from app.core.dependencies import get_current_user, require_roles
from app.models.user import User
from app.schemas.common import APIResponse, PaginationParams, PaginationMeta
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate, PaymentRecord
from app.services.invoice import InvoiceService

router = APIRouter(prefix="/invoices", tags=["Invoices"])


def serialize_invoice(invoice):
    amount = invoice.total_amount or invoice.balance_due or invoice.amount_paid or 0
    return {
        "id": str(invoice.id),
        "invoice_number": invoice.invoice_number,
        "invoiceNumber": invoice.invoice_number,
        "order_id": str(invoice.order_id),
        "orderId": str(invoice.order_id),
        "order_number": invoice.order_number,
        "orderNumber": invoice.order_number,
        "vendor_id": str(invoice.vendor_id),
        "vendorId": str(invoice.vendor_id),
        "vendor_name": invoice.vendor_name,
        "vendorName": invoice.vendor_name,
        "vendor": invoice.vendor_name or str(invoice.vendor_id),
        "status": invoice.status,
        "issue_date": invoice.issue_date,
        "issueDate": invoice.issue_date or invoice.created_at,
        "due_date": invoice.due_date,
        "dueDate": invoice.due_date or invoice.created_at,
        "paid_date": invoice.paid_date,
        "paidDate": invoice.paid_date,
        "subtotal": invoice.subtotal,
        "tax_amount": invoice.tax_amount,
        "taxAmount": invoice.tax_amount,
        "discount": invoice.discount,
        "total_amount": invoice.total_amount,
        "totalAmount": invoice.total_amount,
        "amount": amount,
        "amount_paid": invoice.amount_paid,
        "amountPaid": invoice.amount_paid,
        "balance_due": invoice.balance_due,
        "balanceDue": invoice.balance_due,
        "currency": invoice.currency,
        "notes": invoice.notes,
        "pdf_url": invoice.pdf_url,
        "pdfUrl": invoice.pdf_url,
        "created_at": invoice.created_at,
        "updated_at": invoice.updated_at,
    }


@router.get("/")
async def list_invoices(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    search: str = Query(None),
    status_filter: str = Query(None, alias="status"),
    order_id: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    skip = (page - 1) * per_page
    params = PaginationParams(page=page, per_page=per_page, sort_by=sort_by, sort_order=sort_order)
    service = InvoiceService(db)
    items, total = await service.list(params, skip=skip, search=search, status=status_filter, order_id=order_id)
    total_pages = (total + per_page - 1) // per_page
    meta = PaginationMeta(
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )
    return APIResponse(success=True, message="Invoices retrieved successfully", data=[serialize_invoice(item) for item in items], meta=meta)


@router.get("/overdue/list")
async def get_overdue_invoices(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_roles(["admin", "warehouse_manager"])),
    db: AsyncSession = Depends(get_async_session),
):
    skip = (page - 1) * per_page
    service = InvoiceService(db)
    items, total = await service.get_overdue(skip=skip, per_page=per_page)
    total_pages = (total + per_page - 1) // per_page
    meta = PaginationMeta(
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )
    return APIResponse(success=True, message="Overdue invoices retrieved successfully", data=[serialize_invoice(item) for item in items], meta=meta)


@router.get("/revenue-data")
async def get_revenue_data(
    start_date: str = Query(None),
    end_date: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    service = InvoiceService(db)
    data = await service.get_revenue_data(start_date=start_date, end_date=end_date)
    return APIResponse(success=True, message="Revenue data retrieved successfully", data=data)


@router.get("/{invoice_id}")
async def get_invoice(
    invoice_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    service = InvoiceService(db)
    data = await service.get_by_id(invoice_id)
    return APIResponse(success=True, message="Invoice retrieved successfully", data=serialize_invoice(data))


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_invoice(
    body: InvoiceCreate,
    current_user: User = Depends(require_roles(["admin", "warehouse_manager"])),
    db: AsyncSession = Depends(get_async_session),
):
    service = InvoiceService(db)
    data = await service.create(body)
    return APIResponse(success=True, message="Invoice created successfully", data=serialize_invoice(data))


@router.api_route("/{invoice_id}", methods=["PATCH", "PUT"])
async def update_invoice(
    invoice_id: str,
    body: InvoiceUpdate,
    current_user: User = Depends(require_roles(["admin", "warehouse_manager"])),
    db: AsyncSession = Depends(get_async_session),
):
    service = InvoiceService(db)
    data = await service.update(invoice_id, body)
    return APIResponse(success=True, message="Invoice updated successfully", data=serialize_invoice(data))


@router.delete("/{invoice_id}")
async def delete_invoice(
    invoice_id: str,
    current_user: User = Depends(require_roles(["admin"])),
    db: AsyncSession = Depends(get_async_session),
):
    service = InvoiceService(db)
    await service.delete(invoice_id)
    return APIResponse(success=True, message="Invoice deleted successfully")


@router.post("/{invoice_id}/pay")
async def record_payment(
    invoice_id: str,
    body: PaymentRecord,
    current_user: User = Depends(require_roles(["admin", "warehouse_manager"])),
    db: AsyncSession = Depends(get_async_session),
):
    service = InvoiceService(db)
    data = await service.record_payment(invoice_id, body, current_user)
    return APIResponse(success=True, message="Payment recorded successfully", data=serialize_invoice(data))


@router.get("/{invoice_id}/pdf")
async def download_invoice_pdf(
    invoice_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    service = InvoiceService(db)
    pdf_url = await service.generate_invoice_pdf(invoice_id)
    return JSONResponse({"success": True, "message": "Invoice PDF generated successfully", "data": {"url": pdf_url}})
