import pytest
from httpx import AsyncClient
from app.models.order import PurchaseOrder, PurchaseOrderItem
from app.models.vendor import Vendor
from app.models.product import Product
from app.models.warehouse import Warehouse
from app.models.user import User
from app.core.security import hash_password
from datetime import datetime, timedelta, timezone, date
import uuid


@pytest.mark.asyncio
async def test_create_order(client: AsyncClient, admin_token: str, db_session):
    vendor = Vendor(id=uuid.uuid4(), name="Ord Vendor", company_name="OV LLC",
                    email="ov@test.com", phone="+1-555-7001", address="1 O St",
                    city="O City", state="OS", country="USA", pincode="70001",
                    status="active", contact_person="O P", created_by=uuid.uuid4())
    db_session.add(vendor)
    warehouse = Warehouse(id=uuid.uuid4(), name="Ord WH", code="WH-ORD",
                          address="1 WH St", city="WH City", state="WS",
                          country="USA", pincode="71001", capacity=10000.0,
                          used_capacity=0.0, status="active", manager_id=uuid.uuid4())
    db_session.add(warehouse)
    user = User(id=uuid.uuid4(), email="order@test.com", username="orderuser",
                password_hash=hash_password("Test@123"), full_name="Order User",
                role="admin", is_active=True)
    db_session.add(user)
    await db_session.commit()

    order_data = {
        "vendor_id": str(vendor.id),
        "warehouse_id": str(warehouse.id),
        "priority": "medium",
        "notes": "Test order",
        "expected_delivery_date": str(date.today() + timedelta(days=7)),
    }
    response = await client.post("/api/orders", json=order_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    assert response.json()["data"]["priority"] == "medium"


@pytest.mark.asyncio
async def test_list_orders(client: AsyncClient, admin_token: str):
    response = await client.get("/api/orders", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert "data" in response.json()


@pytest.mark.asyncio
async def test_get_order(client: AsyncClient, admin_token: str, db_session):
    vendor = Vendor(id=uuid.uuid4(), name="G Ord Vendor", company_name="GOV LLC",
                    email="gov@test.com", phone="+1-555-7002", address="2 G St",
                    city="G City", state="GS", country="USA", pincode="70002",
                    status="active", contact_person="G P", created_by=uuid.uuid4())
    db_session.add(vendor)
    warehouse = Warehouse(id=uuid.uuid4(), name="G Ord WH", code="WH-GORD",
                          address="2 WH St", city="WH City", state="WS",
                          country="USA", pincode="71002", capacity=10000.0,
                          used_capacity=0.0, status="active", manager_id=uuid.uuid4())
    db_session.add(warehouse)
    await db_session.commit()

    order = PurchaseOrder(
        id=uuid.uuid4(), order_number="PO-TEST-001", vendor_id=vendor.id,
        warehouse_id=warehouse.id, status="pending", priority="medium",
        subtotal=100.00, tax_amount=8.50, discount=0.0, total_amount=108.50,
        currency="USD", ordered_by=uuid.uuid4(),
        expected_delivery_date=date.today() + timedelta(days=7),
    )
    db_session.add(order)
    await db_session.commit()

    response = await client.get(f"/api/orders/{order.id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.json()["data"]["order_number"] == "PO-TEST-001"


@pytest.mark.asyncio
async def test_update_order(client: AsyncClient, admin_token: str, db_session):
    vendor = Vendor(id=uuid.uuid4(), name="U Ord Vendor", company_name="UOV LLC",
                    email="uov@test.com", phone="+1-555-7003", address="3 U St",
                    city="U City", state="US", country="USA", pincode="70003",
                    status="active", contact_person="U P", created_by=uuid.uuid4())
    db_session.add(vendor)
    warehouse = Warehouse(id=uuid.uuid4(), name="U Ord WH", code="WH-UORD",
                          address="3 WH St", city="WH City", state="WS",
                          country="USA", pincode="71003", capacity=10000.0,
                          used_capacity=0.0, status="active", manager_id=uuid.uuid4())
    db_session.add(warehouse)
    await db_session.commit()

    order = PurchaseOrder(
        id=uuid.uuid4(), order_number="PO-TEST-002", vendor_id=vendor.id,
        warehouse_id=warehouse.id, status="pending", priority="low",
        subtotal=200.00, tax_amount=17.00, discount=0.0, total_amount=217.00,
        currency="USD", ordered_by=uuid.uuid4(),
        expected_delivery_date=date.today() + timedelta(days=14),
    )
    db_session.add(order)
    await db_session.commit()

    response = await client.put(
        f"/api/orders/{order.id}",
        json={"priority": "high"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_approve_order(client: AsyncClient, admin_token: str, db_session):
    vendor = Vendor(id=uuid.uuid4(), name="A Ord Vendor", company_name="AOV LLC",
                    email="aov@test.com", phone="+1-555-7004", address="4 A St",
                    city="A City", state="AS", country="USA", pincode="70004",
                    status="active", contact_person="A P", created_by=uuid.uuid4())
    db_session.add(vendor)
    warehouse = Warehouse(id=uuid.uuid4(), name="A Ord WH", code="WH-AORD",
                          address="4 WH St", city="WH City", state="WS",
                          country="USA", pincode="71004", capacity=10000.0,
                          used_capacity=0.0, status="active", manager_id=uuid.uuid4())
    db_session.add(warehouse)
    await db_session.commit()

    order = PurchaseOrder(
        id=uuid.uuid4(), order_number="PO-TEST-003", vendor_id=vendor.id,
        warehouse_id=warehouse.id, status="pending", priority="urgent",
        subtotal=300.00, tax_amount=25.50, discount=0.0, total_amount=325.50,
        currency="USD", ordered_by=uuid.uuid4(),
        expected_delivery_date=date.today() + timedelta(days=3),
    )
    db_session.add(order)
    await db_session.commit()

    response = await client.put(
        f"/api/orders/{order.id}/approve",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "approved"


@pytest.mark.asyncio
async def test_order_status_distribution(client: AsyncClient, admin_token: str):
    response = await client.get("/api/orders/status-distribution", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
