import pytest
from httpx import AsyncClient
from app.models.shipment import Shipment
from app.models.order import PurchaseOrder
from app.models.vendor import Vendor
from app.models.warehouse import Warehouse
from datetime import datetime, timedelta, timezone, date
import uuid


@pytest.mark.asyncio
async def test_create_shipment(client: AsyncClient, admin_token: str, db_session):
    vendor = Vendor(id=uuid.uuid4(), name="Ship Vendor", company_name="SV LLC",
                    email="sv@test.com", phone="+1-555-9001", address="1 Ship St",
                    city="S City", state="SS", country="USA", pincode="90001",
                    status="active", contact_person="S P", created_by=uuid.uuid4())
    db_session.add(vendor)
    warehouse = Warehouse(id=uuid.uuid4(), name="Ship WH", code="WH-SHIP",
                          address="1 WH St", city="WH City", state="WS",
                          country="USA", pincode="91001", capacity=10000.0,
                          used_capacity=0.0, status="active", manager_id=uuid.uuid4())
    db_session.add(warehouse)
    order = PurchaseOrder(
        id=uuid.uuid4(), order_number="PO-SHP-001", vendor_id=vendor.id,
        warehouse_id=warehouse.id, status="approved", priority="high",
        subtotal=500.00, tax_amount=42.50, discount=0.0, total_amount=542.50,
        currency="USD", ordered_by=uuid.uuid4(),
        expected_delivery_date=date.today() + timedelta(days=5),
    )
    db_session.add(order)
    await db_session.commit()

    shipment_data = {
        "order_id": str(order.id),
        "origin_warehouse_id": str(warehouse.id),
        "carrier": "FedEx",
        "destination_address": "123 Test Ave, Test City, TS 12345",
        "weight": 10.5,
        "dimensions": "12x12x12",
    }
    response = await client.post("/api/shipments", json=shipment_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    assert response.json()["data"]["carrier"] == "FedEx"


@pytest.mark.asyncio
async def test_list_shipments(client: AsyncClient, admin_token: str):
    response = await client.get("/api/shipments", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert "data" in response.json()


@pytest.mark.asyncio
async def test_get_shipment(client: AsyncClient, admin_token: str, db_session):
    vendor = Vendor(id=uuid.uuid4(), name="GS Vendor", company_name="GSV LLC",
                    email="gsv@test.com", phone="+1-555-9002", address="2 GS St",
                    city="GS City", state="GSS", country="USA", pincode="90002",
                    status="active", contact_person="GS P", created_by=uuid.uuid4())
    db_session.add(vendor)
    warehouse = Warehouse(id=uuid.uuid4(), name="GS WH", code="WH-GS",
                          address="2 WH St", city="WH City", state="WS",
                          country="USA", pincode="91002", capacity=10000.0,
                          used_capacity=0.0, status="active", manager_id=uuid.uuid4())
    db_session.add(warehouse)
    order = PurchaseOrder(
        id=uuid.uuid4(), order_number="PO-GS-001", vendor_id=vendor.id,
        warehouse_id=warehouse.id, status="approved", priority="medium",
        subtotal=300.00, tax_amount=25.50, discount=0.0, total_amount=325.50,
        currency="USD", ordered_by=uuid.uuid4(),
        expected_delivery_date=date.today() + timedelta(days=10),
    )
    db_session.add(order)
    await db_session.commit()

    shipment = Shipment(
        id=uuid.uuid4(), tracking_number="SHP-TEST-001", order_id=order.id,
        carrier="UPS", status="pending", origin_warehouse_id=warehouse.id,
        destination_address="456 Test Blvd", weight=5.0,
    )
    db_session.add(shipment)
    await db_session.commit()

    response = await client.get(f"/api/shipments/{shipment.id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.json()["data"]["tracking_number"] == "SHP-TEST-001"


@pytest.mark.asyncio
async def test_update_shipment(client: AsyncClient, admin_token: str, db_session):
    vendor = Vendor(id=uuid.uuid4(), name="US Vendor", company_name="USV LLC",
                    email="usv@test.com", phone="+1-555-9003", address="3 US St",
                    city="US City", state="USS", country="USA", pincode="90003",
                    status="active", contact_person="US P", created_by=uuid.uuid4())
    db_session.add(vendor)
    warehouse = Warehouse(id=uuid.uuid4(), name="US WH", code="WH-US",
                          address="3 WH St", city="WH City", state="WS",
                          country="USA", pincode="91003", capacity=10000.0,
                          used_capacity=0.0, status="active", manager_id=uuid.uuid4())
    db_session.add(warehouse)
    order = PurchaseOrder(
        id=uuid.uuid4(), order_number="PO-US-001", vendor_id=vendor.id,
        warehouse_id=warehouse.id, status="approved", priority="low",
        subtotal=150.00, tax_amount=12.75, discount=0.0, total_amount=162.75,
        currency="USD", ordered_by=uuid.uuid4(),
        expected_delivery_date=date.today() + timedelta(days=14),
    )
    db_session.add(order)
    await db_session.commit()

    shipment = Shipment(
        id=uuid.uuid4(), tracking_number="SHP-TEST-002", order_id=order.id,
        carrier="DHL", status="pending", origin_warehouse_id=warehouse.id,
        destination_address="789 Update Rd", weight=8.0,
    )
    db_session.add(shipment)
    await db_session.commit()

    response = await client.put(
        f"/api/shipments/{shipment.id}",
        json={"carrier": "FedEx"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["carrier"] == "FedEx"


@pytest.mark.asyncio
async def test_update_tracking(client: AsyncClient, admin_token: str, db_session):
    vendor = Vendor(id=uuid.uuid4(), name="TR Vendor", company_name="TRV LLC",
                    email="trv@test.com", phone="+1-555-9004", address="4 TR St",
                    city="TR City", state="TRS", country="USA", pincode="90004",
                    status="active", contact_person="TR P", created_by=uuid.uuid4())
    db_session.add(vendor)
    warehouse = Warehouse(id=uuid.uuid4(), name="TR WH", code="WH-TR",
                          address="4 WH St", city="WH City", state="WS",
                          country="USA", pincode="91004", capacity=10000.0,
                          used_capacity=0.0, status="active", manager_id=uuid.uuid4())
    db_session.add(warehouse)
    order = PurchaseOrder(
        id=uuid.uuid4(), order_number="PO-TR-001", vendor_id=vendor.id,
        warehouse_id=warehouse.id, status="shipped", priority="high",
        subtotal=800.00, tax_amount=68.00, discount=0.0, total_amount=868.00,
        currency="USD", ordered_by=uuid.uuid4(),
        expected_delivery_date=date.today() + timedelta(days=2),
    )
    db_session.add(order)
    await db_session.commit()

    shipment = Shipment(
        id=uuid.uuid4(), tracking_number="SHP-TR-001", order_id=order.id,
        carrier="UPS", status="in_transit", origin_warehouse_id=warehouse.id,
        destination_address="101 Track Ln", weight=15.0,
        current_location="Transit Hub",
    )
    db_session.add(shipment)
    await db_session.commit()

    response = await client.put(
        f"/api/shipments/{shipment.id}/tracking",
        json={"status": "delivered", "current_location": "Destination City"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
