from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler
import os
from pathlib import Path

from app.core.config import settings
from app.core.exceptions import AppException, NotFoundException, UnauthorizedException, ForbiddenException, BadRequestException, ConflictException
from app.api.v1 import api_router
from app.middleware.rate_limit import limiter
from app.ws.manager import manager
from app.utils.file_storage import file_storage

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    for subdir in ["images", "documents", "invoices"]:
        os.makedirs(os.path.join(settings.UPLOAD_DIR, subdir), exist_ok=True)
    # Auto-seed database if empty
    from app.db.seeds.runner import auto_seed_if_empty
    await auto_seed_if_empty()
    yield
    # Shutdown
    pass


app = FastAPI(
    title="SupplySphere API",
    version="1.0.0",
    description="Enterprise Supply Chain Management System API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    return {"message": "SupplySphere Backend Running Successfully"}


app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
if settings.RATE_LIMIT_ENABLED:
    app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def normalize_collection_paths(request: Request, call_next):
    collection_paths = {
        "/api/users",
        "/api/vendors",
        "/api/products",
        "/api/inventory",
        "/api/warehouses",
        "/api/orders",
        "/api/shipments",
        "/api/invoices",
        "/api/notifications",
        "/api/audit-logs",
        "/api/uploads",
    }
    if request.scope.get("path") in collection_paths:
        request.scope["path"] = request.scope["path"] + "/"
    return await call_next(request)


@app.middleware("http")
async def add_error_handler(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except AppException:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "Internal server error", "data": str(e) if settings.DEBUG else None},
        )


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.detail, "detail": exc.detail, "code": exc.code},
    )


@app.middleware("http")
async def log_requests(request: Request, call_next):
    import time
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    print(f"{request.method} {request.url.path} -> {response.status_code} ({duration:.3f}s)")
    return response


app.include_router(api_router, prefix=settings.API_V1_PREFIX)


uploads_path = Path(settings.UPLOAD_DIR).resolve()
if uploads_path.exists():
    app.mount("/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.PROJECT_NAME, "version": settings.VERSION}


@app.websocket("/ws")
async def websocket_endpoint(websocket):
    from app.core.security import decode_token
    from app.repositories.user import UserRepository
    from app.core.database import AsyncSessionLocal

    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001)
        return

    payload = decode_token(token)
    if not payload:
        await websocket.close(code=4001)
        return

    user_id = payload.get("sub")
    role = payload.get("role", "unknown")

    async with AsyncSessionLocal() as db:
        repo = UserRepository(db)
        from uuid import UUID
        user = await repo.get_by_id(UUID(user_id))
        if not user or not user.is_active:
            await websocket.close(code=4001)
            return

    await manager.connect(websocket, user_id, role)

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "")
            if msg_type == "ping":
                await websocket.send_json({"type": "pong"})
            elif msg_type == "subscribe":
                channel = data.get("channel", "")
                await websocket.send_json({"type": "subscribed", "channel": channel})
    except Exception:
        pass
    finally:
        manager.disconnect(user_id, role)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)

