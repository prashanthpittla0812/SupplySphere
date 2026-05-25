from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import Session as SyncSession, sessionmaker
from sqlalchemy import create_engine, event

from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL

IS_SQLITE = "sqlite" in DATABASE_URL


def _get_async_url():
    if IS_SQLITE:
        return DATABASE_URL
    url = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    # asyncpg does not accept sslmode in query string — translate it
    url = url.replace("sslmode=require", "ssl=require")
    url = url.replace("sslmode=prefer", "ssl=prefer")
    url = url.replace("sslmode=disable", "ssl=false")
    return url


def _get_sync_url():
    if IS_SQLITE:
        return DATABASE_URL.replace("sqlite+aiosqlite://", "sqlite://")
    return DATABASE_URL.replace("postgresql://", "postgresql+psycopg://")


ASYNC_DATABASE_URL = _get_async_url()
SYNC_DATABASE_URL = _get_sync_url()

async_engine_kwargs = {"echo": settings.DEBUG}
sync_engine_kwargs = {"echo": settings.DEBUG}

if IS_SQLITE:
    async_engine_kwargs["connect_args"] = {"check_same_thread": False}
    sync_engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    async_engine_kwargs.update(
        {
            "pool_size": 20,
            "max_overflow": 10,
            "pool_pre_ping": True,
            "pool_recycle": 3600,
        }
    )
    sync_engine_kwargs.update(
        {
            "pool_size": 10,
            "max_overflow": 5,
            "pool_pre_ping": True,
            "pool_recycle": 3600,
        }
    )

async_engine = create_async_engine(ASYNC_DATABASE_URL, **async_engine_kwargs)
sync_engine = create_engine(SYNC_DATABASE_URL, **sync_engine_kwargs)

POOL_SIZE = async_engine_kwargs.get("pool_size", 5)
MAX_OVERFLOW = async_engine_kwargs.get("max_overflow", 10)


if IS_SQLITE:

    @event.listens_for(sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


AsyncSessionLocal = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
SyncSessionLocal = sessionmaker(sync_engine, class_=SyncSession, expire_on_commit=False)


async def get_async_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_session() -> SyncSession:
    session = SyncSessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
