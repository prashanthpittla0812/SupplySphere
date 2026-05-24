import pytest
from httpx import AsyncClient
from app.models.vendor import Vendor
from app.models.user import User
from app.core.security import hash_password
import uuid


@pytest.mark.asyncio
async def test_create_vendor(client: AsyncClient, admin_token: str):
    vendor_data = {
        "name": "Test Vendor Inc",
        "company_name": "Test Vendor Inc.",
        "email": "vendor@test.com",
        "phone": "+1-555-9999",
        "address": "123 Vendor St",
        "city": "Test City",
        "state": "TS",
        "country": "USA",
        "pincode": "12345",
        "contact_person": "Test Contact",
    }
    response = await client.post("/api/vendors", json=vendor_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    data = response.json()
    assert data["data"]["email"] == "vendor@test.com"


@pytest.mark.asyncio
async def test_list_vendors(client: AsyncClient, admin_token: str):
    response = await client.get("/api/vendors", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert "data" in response.json()


@pytest.mark.asyncio
async def test_get_vendor(client: AsyncClient, admin_token: str, db_session):
    vendor = Vendor(
        id=uuid.uuid4(),
        name="Get Vendor",
        company_name="Get Vendor LLC",
        email="getv@test.com",
        phone="+1-555-1111",
        address="1 Get St",
        city="G City",
        state="GS",
        country="USA",
        pincode="11111",
        status="active",
        contact_person="G Person",
        created_by=uuid.uuid4(),
    )
    db_session.add(vendor)
    await db_session.commit()

    response = await client.get(f"/api/vendors/{vendor.id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "Get Vendor"


@pytest.mark.asyncio
async def test_update_vendor(client: AsyncClient, admin_token: str, db_session):
    vendor = Vendor(
        id=uuid.uuid4(),
        name="Update Vendor",
        company_name="Update Vendor LLC",
        email="updv@test.com",
        phone="+1-555-2222",
        address="2 Update St",
        city="U City",
        state="US",
        country="USA",
        pincode="22222",
        status="active",
        contact_person="U Person",
        created_by=uuid.uuid4(),
    )
    db_session.add(vendor)
    await db_session.commit()

    response = await client.put(
        f"/api/vendors/{vendor.id}",
        json={"name": "Updated Vendor Name"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "Updated Vendor Name"


@pytest.mark.asyncio
async def test_delete_vendor(client: AsyncClient, admin_token: str, db_session):
    vendor = Vendor(
        id=uuid.uuid4(),
        name="Delete Vendor",
        company_name="Delete Vendor LLC",
        email="delv@test.com",
        phone="+1-555-3333",
        address="3 Delete St",
        city="D City",
        state="DS",
        country="USA",
        pincode="33333",
        status="active",
        contact_person="D Person",
        created_by=uuid.uuid4(),
    )
    db_session.add(vendor)
    await db_session.commit()

    response = await client.delete(f"/api/vendors/{vendor.id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_approve_vendor(client: AsyncClient, admin_token: str, db_session):
    vendor = Vendor(
        id=uuid.uuid4(),
        name="Pending Vendor",
        company_name="Pending Vendor LLC",
        email="pendv@test.com",
        phone="+1-555-4444",
        address="4 Pending St",
        city="P City",
        state="PS",
        country="USA",
        pincode="44444",
        status="pending",
        contact_person="P Person",
        created_by=uuid.uuid4(),
    )
    db_session.add(vendor)
    await db_session.commit()

    response = await client.put(
        f"/api/vendors/{vendor.id}/approve",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "active"


@pytest.mark.asyncio
async def test_reject_vendor(client: AsyncClient, admin_token: str, db_session):
    vendor = Vendor(
        id=uuid.uuid4(),
        name="Reject Vendor",
        company_name="Reject Vendor LLC",
        email="rejv@test.com",
        phone="+1-555-5555",
        address="5 Reject St",
        city="R City",
        state="RS",
        country="USA",
        pincode="55555",
        status="pending",
        contact_person="R Person",
        created_by=uuid.uuid4(),
    )
    db_session.add(vendor)
    await db_session.commit()

    response = await client.put(
        f"/api/vendors/{vendor.id}/reject",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "rejected"
