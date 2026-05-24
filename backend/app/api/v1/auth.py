from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_session
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    RefreshTokenRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
)
from app.schemas.common import APIResponse
from app.schemas.user import UserOut
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _frontend_user(user: User) -> dict:
    role = user.role.value if hasattr(user.role, "value") else user.role
    return {
        "id": str(user.id),
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
        "name": user.full_name,
        "role": role,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
    }


def _frontend_tokens(data: dict) -> dict:
    return {
        "accessToken": data["access_token"],
        "refreshToken": data.get("refresh_token", data["access_token"]),
    }


def _auth_payload(data: dict) -> dict:
    user = _frontend_user(data["user"])
    return {
        "user": user,
        "tokens": _frontend_tokens(data),
        "access_token": data["access_token"],
        "refresh_token": data.get("refresh_token"),
        "token_type": "bearer",
        "id": user["id"],
        "email": user["email"],
        "username": user["username"],
        "full_name": user["full_name"],
        "name": user["name"],
        "role": user["role"],
    }


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_async_session)):
    service = AuthService(db)
    data = await service.register(body)
    return APIResponse(success=True, message="User registered successfully", data=_auth_payload(data))


@router.post("/login")
async def login(body: LoginRequest, request: Request, db: AsyncSession = Depends(get_async_session)):
    service = AuthService(db)
    ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    data = await service.login(body, ip=ip, user_agent=user_agent)
    return APIResponse(success=True, message="Login successful", data=_auth_payload(data))


@router.post("/refresh")
async def refresh(body: RefreshTokenRequest, db: AsyncSession = Depends(get_async_session)):
    service = AuthService(db)
    data = await service.refresh_token(body.refresh_token)
    return APIResponse(
        success=True,
        message="Token refreshed successfully",
        data={
            "accessToken": data["access_token"],
            "refreshToken": data["access_token"],
            "access_token": data["access_token"],
            "token_type": "bearer",
        },
    )


@router.post("/refresh-token")
async def refresh_token_alias(body: RefreshTokenRequest, db: AsyncSession = Depends(get_async_session)):
    return await refresh(body, db)


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_async_session)):
    service = AuthService(db)
    await service.logout(current_user.id)
    return APIResponse(success=True, message="Logout successful")


@router.post("/forgot-password")
async def forgot_password(body: ForgotPasswordRequest, db: AsyncSession = Depends(get_async_session)):
    service = AuthService(db)
    await service.forgot_password(body.email)
    return APIResponse(success=True, message="Password reset email sent if account exists")


@router.post("/reset-password")
async def reset_password(body: ResetPasswordRequest, db: AsyncSession = Depends(get_async_session)):
    service = AuthService(db)
    await service.reset_password(body.token, body.new_password)
    return APIResponse(success=True, message="Password reset successfully")


@router.post("/change-password")
async def change_password(
    body: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    service = AuthService(db)
    await service.change_password(current_user.id, body.current_password, body.new_password)
    return APIResponse(success=True, message="Password changed successfully")


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return APIResponse(success=True, message="Current user retrieved", data=_frontend_user(current_user))
