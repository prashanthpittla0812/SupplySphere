import pytest
from httpx import AsyncClient
from app.core.security import hash_password
from app.models.user import User
import uuid


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient, test_user_data: dict):
    response = await client.post("/api/auth/register", json=test_user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == test_user_data["email"]


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, test_user_data: dict):
    await client.post("/api/auth/register", json=test_user_data)
    response = await client.post("/api/auth/register", json=test_user_data)
    assert response.status_code == 409
    data = response.json()
    assert "already exists" in data.get("detail", "").lower()


@pytest.mark.asyncio
async def test_register_weak_password(client: AsyncClient, test_user_data: dict):
    weak_data = {**test_user_data, "password": "weak"}
    response = await client.post("/api/auth/register", json=weak_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user_data: dict, db_session):
    user = User(
        id=uuid.uuid4(),
        email=test_user_data["email"],
        username=test_user_data["username"],
        password_hash=hash_password(test_user_data["password"]),
        full_name=test_user_data["full_name"],
        role=test_user_data["role"],
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()

    response = await client.post("/api/auth/login", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"],
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data.get("data", {})
    assert data["success"] is True


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, test_user_data: dict, db_session):
    user = User(
        id=uuid.uuid4(),
        email=test_user_data["email"],
        username=test_user_data["username"],
        password_hash=hash_password(test_user_data["password"]),
        full_name=test_user_data["full_name"],
        role=test_user_data["role"],
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()

    response = await client.post("/api/auth/login", json={
        "email": test_user_data["email"],
        "password": "WrongPass@123",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_inactive_user(client: AsyncClient, test_user_data: dict, db_session):
    user = User(
        id=uuid.uuid4(),
        email=test_user_data["email"],
        username=test_user_data["username"],
        password_hash=hash_password(test_user_data["password"]),
        full_name=test_user_data["full_name"],
        role=test_user_data["role"],
        is_active=False,
    )
    db_session.add(user)
    await db_session.commit()

    response = await client.post("/api/auth/login", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"],
    })
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_refresh_success(client: AsyncClient, test_user_data: dict, db_session):
    user = User(
        id=uuid.uuid4(),
        email=test_user_data["email"],
        username=test_user_data["username"],
        password_hash=hash_password(test_user_data["password"]),
        full_name=test_user_data["full_name"],
        role=test_user_data["role"],
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()

    login_resp = await client.post("/api/auth/login", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"],
    })
    refresh_token = login_resp.json()["data"]["refresh_token"]

    response = await client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data.get("data", {})


@pytest.mark.asyncio
async def test_refresh_invalid_token(client: AsyncClient):
    response = await client.post("/api/auth/refresh", json={"refresh_token": "invalid_token"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_forgot_password(client: AsyncClient, test_user_data: dict, db_session):
    user = User(
        id=uuid.uuid4(),
        email=test_user_data["email"],
        username=test_user_data["username"],
        password_hash=hash_password(test_user_data["password"]),
        full_name=test_user_data["full_name"],
        role=test_user_data["role"],
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()

    response = await client.post("/api/auth/forgot-password", json={"email": test_user_data["email"]})
    assert response.status_code in (200, 202)


@pytest.mark.asyncio
async def test_change_password(client: AsyncClient, test_user_data: dict, db_session):
    user = User(
        id=uuid.uuid4(),
        email=test_user_data["email"],
        username=test_user_data["username"],
        password_hash=hash_password(test_user_data["password"]),
        full_name=test_user_data["full_name"],
        role=test_user_data["role"],
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()

    login_resp = await client.post("/api/auth/login", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"],
    })
    token = login_resp.json()["data"]["access_token"]

    response = await client.post("/api/auth/change-password", json={
        "old_password": test_user_data["password"],
        "new_password": "NewPass@6789",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_me(client: AsyncClient, admin_token: str):
    response = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
