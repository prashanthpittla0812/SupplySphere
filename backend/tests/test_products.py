import pytest
from httpx import AsyncClient
from app.models.product import Product
from app.models.vendor import Vendor
import uuid


@pytest.mark.asyncio
async def test_create_product(client: AsyncClient, admin_token: str, db_session):
    vendor = Vendor(
        id=uuid.uuid4(),
        name="Prod Vendor",
        company_name="Prod Vendor LLC",
        email="prodvend@test.com",
        phone="+1-555-0001",
        address="1 Prod St",
        city="P City",
        state="PS",
        country="USA",
        pincode="00001",
        status="active",
        contact_person="P Person",
        created_by=uuid.uuid4(),
    )
    db_session.add(vendor)
    await db_session.commit()

    product_data = {
        "name": "New Product",
        "sku": f"PRD-{uuid.uuid4().hex[:6].upper()}",
        "category": "Electronics",
        "unit_price": 49.99,
        "unit_cost": 25.00,
        "unit": "pcs",
        "vendor_id": str(vendor.id),
    }
    response = await client.post("/api/products", json=product_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    assert response.json()["data"]["name"] == "New Product"


@pytest.mark.asyncio
async def test_list_products(client: AsyncClient, admin_token: str):
    response = await client.get("/api/products", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert "data" in response.json()


@pytest.mark.asyncio
async def test_get_product(client: AsyncClient, admin_token: str, db_session):
    vendor = Vendor(
        id=uuid.uuid4(), name="G Prod Vendor", company_name="GPV LLC",
        email="gpv@test.com", phone="+1-555-0002", address="2 G St",
        city="G City", state="GS", country="USA", pincode="00002",
        status="active", contact_person="G P", created_by=uuid.uuid4(),
    )
    db_session.add(vendor)
    await db_session.commit()

    product = Product(
        id=uuid.uuid4(), name="Get Product", sku=f"GET-{uuid.uuid4().hex[:6].upper()}",
        category="Office Supplies", unit_price=19.99, unit_cost=10.00,
        unit="pcs", vendor_id=vendor.id, is_active=True,
    )
    db_session.add(product)
    await db_session.commit()

    response = await client.get(f"/api/products/{product.id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "Get Product"


@pytest.mark.asyncio
async def test_update_product(client: AsyncClient, admin_token: str, db_session):
    vendor = Vendor(
        id=uuid.uuid4(), name="U Prod Vendor", company_name="UPV LLC",
        email="upv@test.com", phone="+1-555-0003", address="3 U St",
        city="U City", state="US", country="USA", pincode="00003",
        status="active", contact_person="U P", created_by=uuid.uuid4(),
    )
    db_session.add(vendor)
    await db_session.commit()

    product = Product(
        id=uuid.uuid4(), name="Update Product", sku=f"UPD-{uuid.uuid4().hex[:6].upper()}",
        category="Electronics", unit_price=99.99, unit_cost=50.00,
        unit="pcs", vendor_id=vendor.id, is_active=True,
    )
    db_session.add(product)
    await db_session.commit()

    response = await client.put(
        f"/api/products/{product.id}",
        json={"unit_price": 79.99},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["unit_price"] == 79.99


@pytest.mark.asyncio
async def test_delete_product(client: AsyncClient, admin_token: str, db_session):
    vendor = Vendor(
        id=uuid.uuid4(), name="D Prod Vendor", company_name="DPV LLC",
        email="dpv@test.com", phone="+1-555-0004", address="4 D St",
        city="D City", state="DS", country="USA", pincode="00004",
        status="active", contact_person="D P", created_by=uuid.uuid4(),
    )
    db_session.add(vendor)
    await db_session.commit()

    product = Product(
        id=uuid.uuid4(), name="Delete Product", sku=f"DEL-{uuid.uuid4().hex[:6].upper()}",
        category="Industrial", unit_price=199.99, unit_cost=100.00,
        unit="pcs", vendor_id=vendor.id, is_active=True,
    )
    db_session.add(product)
    await db_session.commit()

    response = await client.delete(f"/api/products/{product.id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_search_products(client: AsyncClient, admin_token: str, db_session):
    vendor = Vendor(
        id=uuid.uuid4(), name="S Prod Vendor", company_name="SPV LLC",
        email="spv@test.com", phone="+1-555-0005", address="5 S St",
        city="S City", state="SS", country="USA", pincode="00005",
        status="active", contact_person="S P", created_by=uuid.uuid4(),
    )
    db_session.add(vendor)
    await db_session.commit()

    for name in ["Alpha Widget", "Beta Widget", "Gamma Gadget"]:
        db_session.add(Product(
            id=uuid.uuid4(), name=name, sku=f"{name[:4].upper()}-{uuid.uuid4().hex[:6].upper()}",
            category="Widgets", unit_price=29.99, unit_cost=15.00,
            unit="pcs", vendor_id=vendor.id, is_active=True,
        ))
    await db_session.commit()

    response = await client.get("/api/products/search?q=Widget", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    results = response.json()["data"]
    assert len(results) >= 2
