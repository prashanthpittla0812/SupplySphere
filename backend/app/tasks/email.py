from app.tasks.celery_app import celery_app
from app.core.config import settings
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_email(self, to_email: str, subject: str, body: str, html_body: Optional[str] = None):
    """Send email via SMTP"""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.EMAIL_FROM
        msg["To"] = to_email
        msg.attach(MIMEText(body, "plain"))
        if html_body:
            msg.attach(MIMEText(html_body, "html"))
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        return {"success": True, "to": to_email, "subject": subject}
    except Exception as exc:
        raise self.retry(exc=exc)

@celery_app.task
def send_welcome_email(user_email: str, user_name: str):
    body = f"Welcome to SupplySphere, {user_name}!\n\nYour account has been created successfully."
    send_email.delay(user_email, "Welcome to SupplySphere", body)

@celery_app.task
def send_password_reset_email(user_email: str, reset_token: str):
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
    body = f"Click the link to reset your password: {reset_url}"
    send_email.delay(user_email, "Password Reset - SupplySphere", body)

@celery_app.task
def send_invoice_email(user_email: str, invoice_number: str, pdf_url: Optional[str] = None):
    body = f"Invoice {invoice_number} has been generated.\n\nYou can view it in your account."
    if pdf_url:
        body += f"\nDownload: {pdf_url}"
    send_email.delay(user_email, f"Invoice {invoice_number} - SupplySphere", body)

@celery_app.task
def send_low_stock_alert(product_name: str, current_stock: float, min_level: float):
    body = f"LOW STOCK ALERT: {product_name}\nCurrent Stock: {current_stock}\nMinimum Level: {min_level}"
    recipients = settings.ALERT_EMAIL_RECIPIENTS if hasattr(settings, 'ALERT_EMAIL_RECIPIENTS') else []
    for email in recipients:
        send_email.delay(email, f"Low Stock Alert - {product_name}", body)

@celery_app.task
def send_order_confirmation(user_email: str, order_number: str, order_details: dict):
    body = f"Order {order_number} has been confirmed.\n\nTotal: ${order_details.get('total_amount', 0):.2f}"
    send_email.delay(user_email, f"Order Confirmation - {order_number}", body)
