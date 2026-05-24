from typing import Optional, List
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_session
from app.core.security import decode_token
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.repositories.user import UserRepository

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_async_session),
):
    if not credentials:
        raise UnauthorizedException("Not authenticated")
    payload = decode_token(credentials.credentials)
    if not payload or payload.get("token_type") != "access":
        raise UnauthorizedException("Invalid or expired token")
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedException("Invalid token payload")
    repo = UserRepository(db)
    user = await repo.get_by_id(UUID(user_id_str))
    if not user or user.is_deleted:
        raise UnauthorizedException("User not found or deactivated")
    return user


def require_roles(allowed_roles: List[str]):
    async def role_checker(current_user=Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise ForbiddenException(f"Requires one of roles: {', '.join(allowed_roles)}")
        return current_user
    return role_checker


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_async_session),
):
    if not credentials:
        return None
    payload = decode_token(credentials.credentials)
    if not payload or payload.get("token_type") != "access":
        return None
    user_id_str = payload.get("sub")
    if not user_id_str:
        return None
    repo = UserRepository(db)
    user = await repo.get_by_id(UUID(user_id_str))
    if not user or user.is_deleted:
        return None
    return user
