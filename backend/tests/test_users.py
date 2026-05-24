import pytest
from httpx import AsyncClient
from app.core.security import hash_password
from app.models.user import User
import uuid


@pytest.mark.asyncio
async def test_list_users(client: AsyncClient, admin_token: str):
    response = await client.get("/api/users", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


@pytest.mark.asyncio
async def test_get_user(client: AsyncClient, admin_token: str, db_session):
    user = User(
        id=uuid.uuid4(),
        email="getuser@test.com",
        username="getuser",
        password_hash=hash_password("Test@12345"),
        full_name="Get User",
        role="vendor",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()

    response = await client.get(f"/api/users/{user.id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.json()["data"]["email"] == "getuser@test.com"


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient, admin_token: str):
    user_data = {
        "email": "newuser@test.com",
        "username": "newuser",
        "password": "NewUser@123",
        "full_name": "New User",
        "role": "vendor",
    }
    response = await client.post("/api/users", json=user_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_update_user(client: AsyncClient, admin_token: str, db_session):
    user = User(
        id=uuid.uuid4(),
        email="updateuser@test.com",
        username="updateuser",
        password_hash=hash_password("Test@12345"),
        full_name="Update User",
        role="vendor",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()

    response = await client.put(
        f"/api/users/{user.id}",
        json={"full_name": "Updated Name"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["full_name"] == "Updated Name"


@pytest.mark.asyncio
async def test_delete_user(client: AsyncClient, admin_token: str, db_session):
    user = User(
        id=uuid.uuid4(),
        email="deleteuser@test.com",
        username="deleteuser",
        password_hash=hash_password("Test@12345"),
        full_name="Delete User",
        role="vendor",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()

    response = await client.delete(f"/api/users/{user.id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    response = await client.get("/api/users")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_forbidden_access(client: AsyncClient, vendor_token: str):
    response = await client.get("/api/users", headers={"Authorization": f"Bearer {vendor_token}"})
    assert response.status_code == 403
