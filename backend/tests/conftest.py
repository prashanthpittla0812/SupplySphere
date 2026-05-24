import pytest
import pytest_asyncio
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from app.models.base import Base
from app.main import app
from app.core.database import get_async_session
from app.core.config import settings
from app.core.security import create_access_token
from app.models.user import User
from app.core.security import hash_password
import uuid

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
test_engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_async_session


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session


async def _token_for_role(role: str, db_session: AsyncSession) -> str:
    user = User(
        id=uuid.uuid4(),
        email=f"{role}-{uuid.uuid4().hex[:8]}@test.com",
        username=f"{role}_{uuid.uuid4().hex[:8]}",
        hashed_password=hash_password("Test@12345"),
        full_name=f"{role.replace('_', ' ').title()} Test",
        role=role,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    return create_access_token({"sub": str(user.id), "role": role})


@pytest_asyncio.fixture
async def admin_token(db_session: AsyncSession) -> str:
    return await _token_for_role("admin", db_session)


@pytest_asyncio.fixture
async def warehouse_token(db_session: AsyncSession) -> str:
    return await _token_for_role("warehouse_manager", db_session)


@pytest_asyncio.fixture
async def vendor_token(db_session: AsyncSession) -> str:
    return await _token_for_role("vendor", db_session)


@pytest_asyncio.fixture
async def delivery_token(db_session: AsyncSession) -> str:
    return await _token_for_role("delivery_personnel", db_session)


@pytest.fixture
def test_user_data():
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "Test@12345",
        "full_name": "Test User",
        "phone": "+1234567890",
        "role": "admin",
    }


@pytest.fixture
def test_product_data():
    return {
        "name": "Test Product",
        "sku": f"TST-{uuid.uuid4().hex[:6].upper()}",
        "category": "Electronics",
        "unit_price": 99.99,
        "unit_cost": 50.00,
        "unit": "pcs",
    }
