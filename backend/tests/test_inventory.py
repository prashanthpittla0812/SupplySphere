import pytest
from httpx import AsyncClient
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.warehouse import Warehouse
from app.models.vendor import Vendor
import uuid


@pytest.mark.asyncio
async def test_list_inventory(client: AsyncClient, admin_token: str):
    response = await client.get("/api/inventory", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert "data" in response.json()


@pytest.mark.asyncio
async def test_get_inventory_item(client: AsyncClient, admin_token: str, db_session):
    vendor = Vendor(id=uuid.uuid4(), name="Inv Vendor", company_name="IV LLC",
                    email="iv@test.com", phone="+1-555-8001", address="1 I St",
                    city="I City", state="IS", country="USA", pincode="80001",
                    status="active", contact_person="I P", created_by=uuid.uuid4())
    db_session.add(vendor)
    product = Product(id=uuid.uuid4(), name="Inv Product", sku=f"INV-{uuid.uuid4().hex[:6].upper()}",
                      category="Electronics", unit_price=49.99, unit_cost=25.00,
                      unit="pcs", vendor_id=vendor.id, is_active=True)
    db_session.add(product)
    warehouse = Warehouse(id=uuid.uuid4(), name="Inv WH", code="WH-INV",
                          address="1 WH St", city="WH City", state="WS",
                          country="USA", pincode="81001", capacity=10000.0,
                          used_capacity=0.0, status="active", manager_id=uuid.uuid4())
    db_session.add(warehouse)
    await db_session.commit()

    inv = Inventory(id=uuid.uuid4(), product_id=product.id, warehouse_id=warehouse.id,
                    quantity=100.0, reserved_quantity=10.0)
    db_session.add(inv)
    await db_session.commit()

    response = await client.get(f"/api/inventory/{inv.id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.json()["data"]["quantity"] == 100.0


@pytest.mark.asyncio
async def test_update_inventory(client: AsyncClient, admin_token: str, db_session):
    vendor = Vendor(id=uuid.uuid4(), name="U Inv Vendor", company_name="UIV LLC",
                    email="uiv@test.com", phone="+1-555-8002", address="2 U St",
                    city="U City", state="US", country="USA", pincode="80002",
                    status="active", contact_person="U P", created_by=uuid.uuid4())
    db_session.add(vendor)
    product = Product(id=uuid.uuid4(), name="U Inv Product", sku=f"UIN-{uuid.uuid4().hex[:6].upper()}",
                      category="Office", unit_price=29.99, unit_cost=15.00,
                      unit="pcs", vendor_id=vendor.id, is_active=True)
    db_session.add(product)
    warehouse = Warehouse(id=uuid.uuid4(), name="U Inv WH", code="WH-UINV",
                          address="2 WH St", city="WH City", state="WS",
                          country="USA", pincode="81002", capacity=10000.0,
                          used_capacity=0.0, status="active", manager_id=uuid.uuid4())
    db_session.add(warehouse)
    await db_session.commit()

    inv = Inventory(id=uuid.uuid4(), product_id=product.id, warehouse_id=warehouse.id,
                    quantity=50.0, reserved_quantity=5.0)
    db_session.add(inv)
    await db_session.commit()

    response = await client.put(
        f"/api/inventory/{inv.id}",
        json={"quantity": 75.0},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["quantity"] == 75.0


@pytest.mark.asyncio
async def test_stock_adjustment_increase(client: AsyncClient, admin_token: str, db_session):
    vendor = Vendor(id=uuid.uuid4(), name="S Inv Vendor", company_name="SIV LLC",
                    email="siv@test.com", phone="+1-555-8003", address="3 S St",
                    city="S City", state="SS", country="USA", pincode="80003",
                    status="active", contact_person="S P", created_by=uuid.uuid4())
    db_session.add(vendor)
    product = Product(id=uuid.uuid4(), name="S Inv Product", sku=f"SIN-{uuid.uuid4().hex[:6].upper()}",
                      category="Safety", unit_price=19.99, unit_cost=8.00,
                      unit="pcs", vendor_id=vendor.id, is_active=True)
    db_session.add(product)
    warehouse = Warehouse(id=uuid.uuid4(), name="S Inv WH", code="WH-SINV",
                          address="3 WH St", city="WH City", state="WS",
                          country="USA", pincode="81003", capacity=10000.0,
                          used_capacity=0.0, status="active", manager_id=uuid.uuid4())
    db_session.add(warehouse)
    await db_session.commit()

    inv = Inventory(id=uuid.uuid4(), product_id=product.id, warehouse_id=warehouse.id,
                    quantity=30.0, reserved_quantity=0.0)
    db_session.add(inv)
    await db_session.commit()

    response = await client.post(
        f"/api/inventory/{inv.id}/adjust",
        json={"quantity": 20.0, "type": "add"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["quantity"] == 50.0


@pytest.mark.asyncio
async def test_stock_adjustment_decrease(client: AsyncClient, admin_token: str, db_session):
    vendor = Vendor(id=uuid.uuid4(), name="D Inv Vendor", company_name="DIV LLC",
                    email="div@test.com", phone="+1-555-8004", address="4 D St",
                    city="D City", state="DS", country="USA", pincode="80004",
                    status="active", contact_person="D P", created_by=uuid.uuid4())
    db_session.add(vendor)
    product = Product(id=uuid.uuid4(), name="D Inv Product", sku=f"DIN-{uuid.uuid4().hex[:6].upper()}",
                      category="Packaging", unit_price=9.99, unit_cost=4.00,
                      unit="pcs", vendor_id=vendor.id, is_active=True)
    db_session.add(product)
    warehouse = Warehouse(id=uuid.uuid4(), name="D Inv WH", code="WH-DINV",
                          address="4 WH St", city="WH City", state="WS",
                          country="USA", pincode="81004", capacity=10000.0,
                          used_capacity=0.0, status="active", manager_id=uuid.uuid4())
    db_session.add(warehouse)
    await db_session.commit()

    inv = Inventory(id=uuid.uuid4(), product_id=product.id, warehouse_id=warehouse.id,
                    quantity=40.0, reserved_quantity=0.0)
    db_session.add(inv)
    await db_session.commit()

    response = await client.post(
        f"/api/inventory/{inv.id}/adjust",
        json={"quantity": 10.0, "type": "remove"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["quantity"] == 30.0
