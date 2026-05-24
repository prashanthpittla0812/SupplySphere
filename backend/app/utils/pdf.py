from typing import Optional
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
import os
from pathlib import Path
from datetime import datetime

def generate_invoice_pdf(
    invoice_data: dict,
    company_name: str = "SupplySphere Inc.",
    output_dir: str = "./uploads/invoices"
) -> str:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    filename = f"invoice_{invoice_data.get('invoice_number', 'unknown')}.pdf"
    filepath = os.path.join(output_dir, filename)
    
    doc = SimpleDocTemplate(filepath, pagesize=A4, topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    elements = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle', parent=styles['Heading1'],
        fontSize=24, textColor=colors.HexColor('#1a56db'),
        spaceAfter=20, alignment=TA_CENTER
    )
    elements.append(Paragraph(f"INVOICE", title_style))
    elements.append(Spacer(1, 10))
    
    # Invoice info
    info_data = [
        [f"Invoice #: {invoice_data.get('invoice_number', 'N/A')}", f"Date: {invoice_data.get('issue_date', 'N/A')}"],
        [f"Status: {invoice_data.get('status', 'draft').upper()}", f"Due Date: {invoice_data.get('due_date', 'N/A')}"],
    ]
    info_table = Table(info_data, colWidths=[3*inch, 3*inch])
    info_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#374151')),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 20))
    
    # Vendor info
    elements.append(Paragraph("From:", styles['Heading3']))
    vendor = invoice_data.get('vendor', {})
    vendor_lines = [
        vendor.get('company_name', vendor.get('name', 'N/A')),
        vendor.get('address', ''),
        f"{vendor.get('city', '')}, {vendor.get('state', '')} {vendor.get('pincode', '')}",
        f"GST: {vendor.get('gst_number', 'N/A')}",
    ]
    for line in vendor_lines:
        if line:
            elements.append(Paragraph(line, styles['Normal']))
    elements.append(Spacer(1, 15))
    
    # Order info
    elements.append(Paragraph(f"Order #: {invoice_data.get('order_number', 'N/A')}", styles['Normal']))
    elements.append(Spacer(1, 15))
    
    # Items table
    items = invoice_data.get('items', [])
    table_data = [['#', 'Product', 'Quantity', 'Unit Price', 'Total']]
    for i, item in enumerate(items, 1):
        table_data.append([
            str(i),
            item.get('product_name', 'N/A'),
            str(item.get('quantity', 0)),
            f"${item.get('unit_price', 0):.2f}",
            f"${item.get('total_price', 0):.2f}",
        ])
    
    col_widths = [0.5*inch, 3*inch, 1*inch, 1.2*inch, 1.2*inch]
    items_table = Table(table_data, colWidths=col_widths)
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a56db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 20))
    
    # Totals
    total_style = ParagraphStyle('Total', parent=styles['Normal'], fontSize=12, spaceAfter=4)
    elements.append(Paragraph(f"Subtotal: ${invoice_data.get('subtotal', 0):.2f}", total_style))
    if invoice_data.get('discount', 0):
        elements.append(Paragraph(f"Discount: ${invoice_data.get('discount', 0):.2f}", total_style))
    elements.append(Paragraph(f"Tax: ${invoice_data.get('tax_amount', 0):.2f}", total_style))
    
    grand_total_style = ParagraphStyle(
        'GrandTotal', parent=styles['Heading2'],
        fontSize=14, textColor=colors.HexColor('#1a56db'),
        spaceBefore=10, spaceAfter=4
    )
    elements.append(Paragraph(f"Total Amount: ${invoice_data.get('total_amount', 0):.2f}", grand_total_style))
    
    if invoice_data.get('amount_paid', 0) > 0:
        elements.append(Paragraph(f"Amount Paid: ${invoice_data.get('amount_paid', 0):.2f}", total_style))
        balance = invoice_data.get('total_amount', 0) - invoice_data.get('amount_paid', 0)
        balance_style = ParagraphStyle(
            'Balance', parent=styles['Heading3'],
            fontSize=12, textColor=colors.HexColor('#dc2626')
        )
        elements.append(Paragraph(f"Balance Due: ${balance:.2f}", balance_style))
    
    # Notes
    if invoice_data.get('notes'):
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Notes:", styles['Heading3']))
        elements.append(Paragraph(invoice_data['notes'], styles['Normal']))
    
    # Footer
    elements.append(Spacer(1, 30))
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.gray, alignment=TA_CENTER)
    elements.append(Paragraph(f"Generated by SupplySphere on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))
    elements.append(Paragraph(company_name, footer_style))
    
    doc.build(elements)
    return filepath
