import pytest
from httpx import AsyncClient
from app.models.invoice import Invoice
from app.models.order import PurchaseOrder
from app.models.vendor import Vendor
from app.models.warehouse import Warehouse
from datetime import date, timedelta
import uuid


@pytest.mark.asyncio
async def test_create_invoice(client: AsyncClient, admin_token: str, db_session):
    vendor = Vendor(id=uuid.uuid4(), name="Inv Vendor", company_name="INV LLC",
                    email="inv@test.com", phone="+1-555-6001", address="1 Inv St",
                    city="I City", state="IS", country="USA", pincode="60001",
                    status="active", contact_person="I P", created_by=uuid.uuid4())
    db_session.add(vendor)
    warehouse = Warehouse(id=uuid.uuid4(), name="Inv WH", code="WH-INV",
                          address="1 WH St", city="WH City", state="WS",
                          country="USA", pincode="61001", capacity=10000.0,
                          used_capacity=0.0, status="active", manager_id=uuid.uuid4())
    db_session.add(warehouse)
    order = PurchaseOrder(
        id=uuid.uuid4(), order_number="PO-INV-001", vendor_id=vendor.id,
        warehouse_id=warehouse.id, status="delivered", priority="medium",
        subtotal=1000.00, tax_amount=85.00, discount=0.0, total_amount=1085.00,
        currency="USD", ordered_by=uuid.uuid4(),
        expected_delivery_date=date.today() - timedelta(days=1),
        delivered_date=date.today(),
    )
    db_session.add(order)
    await db_session.commit()

    invoice_data = {
        "order_id": str(order.id),
        "vendor_id": str(vendor.id),
        "subtotal": 1000.00,
        "tax_amount": 85.00,
        "total_amount": 1085.00,
        "due_date": str(date.today() + timedelta(days=30)),
    }
    response = await client.post("/api/invoices", json=invoice_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    assert response.json()["data"]["status"] == "draft"


@pytest.mark.asyncio
async def test_list_invoices(client: AsyncClient, admin_token: str):
    response = await client.get("/api/invoices", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert "data" in response.json()


@pytest.mark.asyncio
async def test_get_invoice(client: AsyncClient, admin_token: str, db_session):
    vendor = Vendor(id=uuid.uuid4(), name="GI Vendor", company_name="GIV LLC",
                    email="giv@test.com", phone="+1-555-6002", address="2 GI St",
                    city="GI City", state="GIS", country="USA", pincode="60002",
                    status="active", contact_person="GI P", created_by=uuid.uuid4())
    db_session.add(vendor)
    warehouse = Warehouse(id=uuid.uuid4(), name="GI WH", code="WH-GI",
                          address="2 WH St", city="WH City", state="WS",
                          country="USA", pincode="61002", capacity=10000.0,
                          used_capacity=0.0, status="active", manager_id=uuid.uuid4())
    db_session.add(warehouse)
    order = PurchaseOrder(
        id=uuid.uuid4(), order_number="PO-GI-001", vendor_id=vendor.id,
        warehouse_id=warehouse.id, status="delivered", priority="medium",
        subtotal=500.00, tax_amount=42.50, discount=0.0, total_amount=542.50,
        currency="USD", ordered_by=uuid.uuid4(),
        expected_delivery_date=date.today() - timedelta(days=2),
        delivered_date=date.today() - timedelta(days=1),
    )
    db_session.add(order)
    await db_session.commit()

    invoice = Invoice(
        id=uuid.uuid4(), invoice_number="INV-TEST-001", order_id=order.id,
        vendor_id=vendor.id, status="draft",
        issue_date=date.today(), due_date=date.today() + timedelta(days=30),
        subtotal=500.00, tax_amount=42.50, discount=0.0, total_amount=542.50,
        amount_paid=0.0, balance_due=542.50, created_by=uuid.uuid4(),
    )
    db_session.add(invoice)
    await db_session.commit()

    response = await client.get(f"/api/invoices/{invoice.id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.json()["data"]["invoice_number"] == "INV-TEST-001"


@pytest.mark.asyncio
async def test_update_invoice(client: AsyncClient, admin_token: str, db_session):
    vendor = Vendor(id=uuid.uuid4(), name="UI Vendor", company_name="UIV LLC",
                    email="uiv2@test.com", phone="+1-555-6003", address="3 UI St",
                    city="UI City", state="UIS", country="USA", pincode="60003",
                    status="active", contact_person="UI P", created_by=uuid.uuid4())
    db_session.add(vendor)
    warehouse = Warehouse(id=uuid.uuid4(), name="UI WH", code="WH-UI",
                          address="3 WH St", city="WH City", state="WS",
                          country="USA", pincode="61003", capacity=10000.0,
                          used_capacity=0.0, status="active", manager_id=uuid.uuid4())
    db_session.add(warehouse)
    order = PurchaseOrder(
        id=uuid.uuid4(), order_number="PO-UI-001", vendor_id=vendor.id,
        warehouse_id=warehouse.id, status="delivered", priority="medium",
        subtotal=750.00, tax_amount=63.75, discount=0.0, total_amount=813.75,
        currency="USD", ordered_by=uuid.uuid4(),
        expected_delivery_date=date.today() - timedelta(days=3),
        delivered_date=date.today() - timedelta(days=2),
    )
    db_session.add(order)
    await db_session.commit()

    invoice = Invoice(
        id=uuid.uuid4(), invoice_number="INV-UI-001", order_id=order.id,
        vendor_id=vendor.id, status="draft",
        issue_date=date.today(), due_date=date.today() + timedelta(days=30),
        subtotal=750.00, tax_amount=63.75, discount=0.0, total_amount=813.75,
        amount_paid=0.0, balance_due=813.75, created_by=uuid.uuid4(),
    )
    db_session.add(invoice)
    await db_session.commit()

    response = await client.put(
        f"/api/invoices/{invoice.id}",
        json={"discount": 50.0},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_pay_invoice(client: AsyncClient, admin_token: str, db_session):
    vendor = Vendor(id=uuid.uuid4(), name="Pay Vendor", company_name="PV LLC",
                    email="pv@test.com", phone="+1-555-6004", address="4 Pay St",
                    city="P City", state="PS", country="USA", pincode="60004",
                    status="active", contact_person="P P", created_by=uuid.uuid4())
    db_session.add(vendor)
    warehouse = Warehouse(id=uuid.uuid4(), name="Pay WH", code="WH-PAY",
                          address="4 WH St", city="WH City", state="WS",
                          country="USA", pincode="61004", capacity=10000.0,
                          used_capacity=0.0, status="active", manager_id=uuid.uuid4())
    db_session.add(warehouse)
    order = PurchaseOrder(
        id=uuid.uuid4(), order_number="PO-PAY-001", vendor_id=vendor.id,
        warehouse_id=warehouse.id, status="delivered", priority="medium",
        subtotal=2000.00, tax_amount=170.00, discount=0.0, total_amount=2170.00,
        currency="USD", ordered_by=uuid.uuid4(),
        expected_delivery_date=date.today() - timedelta(days=5),
        delivered_date=date.today() - timedelta(days=4),
    )
    db_session.add(order)
    await db_session.commit()

    invoice = Invoice(
        id=uuid.uuid4(), invoice_number="INV-PAY-001", order_id=order.id,
        vendor_id=vendor.id, status="sent",
        issue_date=date.today() - timedelta(days=10),
        due_date=date.today() + timedelta(days=20),
        subtotal=2000.00, tax_amount=170.00, discount=0.0, total_amount=2170.00,
        amount_paid=0.0, balance_due=2170.00, created_by=uuid.uuid4(),
    )
    db_session.add(invoice)
    await db_session.commit()

    response = await client.post(
        f"/api/invoices/{invoice.id}/pay",
        json={"amount": 2170.00},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == "paid"
    assert data["amount_paid"] == 2170.00
