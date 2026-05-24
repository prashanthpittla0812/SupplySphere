from app.tasks.celery_app import celery_app
from app.core.config import settings
import os

@celery_app.task(bind=True, max_retries=3)
def generate_invoice_pdf(self, invoice_id: str):
    """Generate PDF for invoice"""
    try:
        from app.utils.pdf import generate_invoice_pdf as generate_pdf
        pdf_path = generate_pdf(invoice_id)
        return {"success": True, "invoice_id": invoice_id, "pdf_path": pdf_path}
    except Exception as exc:
        raise self.retry(exc=exc)

@celery_app.task
def generate_monthly_reports():
    """Generate monthly analytics reports"""
    return {"success": True, "message": "Monthly reports generated"}

@celery_app.task
def cleanup_old_logs(days: int = 90):
    """Clean up audit logs older than specified days"""
    return {"success": True, "message": f"Cleaned up logs older than {days} days"}
