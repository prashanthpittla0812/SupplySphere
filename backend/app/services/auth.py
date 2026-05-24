import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.auth import RegisterRequest, LoginRequest
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.config import settings
from app.core.exceptions import ConflictException, UnauthorizedException, BadRequestException, NotFoundException, ForbiddenException
from app.services.audit_log import AuditLogService


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.audit_log_service = AuditLogService(db)

    async def register(self, data: RegisterRequest) -> dict:
        existing_email = await self.user_repo.get_by_email(data.email)
        if existing_email:
            raise ConflictException("Email already exists")
        existing_username = await self.user_repo.get_by_username(data.username)
        if existing_username:
            raise ConflictException("Username already taken")

        user = await self.user_repo.create(
            email=data.email,
            username=data.username,
            full_name=data.full_name,
            phone=data.phone,
            role=data.role,
            hashed_password=hash_password(data.password),
        )

        tokens = await self._create_tokens(user)
        await self.audit_log_service.log_action(
            user_id=user.id,
            action="register",
            entity_type="user",
            entity_id=user.id,
            changes={"email": data.email, "username": data.username},
            ip_address=None,
            user_agent=None,
            description="User registered successfully",
        )
        return {
            "user": user,
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
        }

    async def login(self, data: LoginRequest, ip: str = None, user_agent: str = None) -> dict:
        user = await self.user_repo.get_by_email(data.email)
        if not user:
            raise UnauthorizedException("Invalid email or password")
        if not user.is_active:
            raise ForbiddenException("Account is deactivated")
        if not verify_password(data.password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password")

        tokens = await self._create_tokens(user)
        await self.audit_log_service.log_action(
            user_id=user.id,
            action="login",
            entity_type="user",
            entity_id=user.id,
            changes=None,
            ip_address=ip,
            user_agent=user_agent,
            description="User logged in",
        )
        return {
            "user": user,
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
        }

    async def refresh_token(self, refresh_token: str) -> dict:
        payload = decode_token(refresh_token)
        if not payload or payload.get("token_type") != "refresh":
            raise UnauthorizedException("Invalid or expired refresh token")

        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedException("Invalid token payload")

        try:
            user_id = uuid.UUID(user_id)
        except ValueError:
            raise UnauthorizedException("Invalid token payload")

        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise UnauthorizedException("User not found or inactive")
        if user.refresh_token != refresh_token:
            raise UnauthorizedException("Refresh token has been revoked")

        access_token = create_access_token({"sub": str(user.id), "role": user.role.value if hasattr(user.role, 'value') else user.role})
        return {"access_token": access_token, "token_type": "bearer"}

    async def logout(self, user_id: uuid.UUID, refresh_token: str = None) -> bool:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")
        await self.user_repo.update(user_id, refresh_token=None)
        return True

    async def forgot_password(self, email: str) -> bool:
        user = await self.user_repo.get_by_email(email)
        if not user:
            return True
        token = self._generate_reset_token()
        expires = datetime.now(timezone.utc) + timedelta(hours=1)
        await self.user_repo.update(user.id, reset_token=token, reset_token_expires=expires)
        return True

    async def reset_password(self, token: str, new_password: str) -> bool:
        from sqlalchemy import select
        query = select(User).where(User.reset_token == token, User.is_deleted == False)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        if not user:
            raise BadRequestException("Invalid reset token")
        if not user.reset_token_expires or user.reset_token_expires < datetime.now(timezone.utc):
            raise BadRequestException("Reset token has expired")

        await self.user_repo.update(user.id, hashed_password=hash_password(new_password), reset_token=None, reset_token_expires=None)
        return True

    async def change_password(self, user_id: uuid.UUID, current_password: str, new_password: str) -> bool:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")
        if not verify_password(current_password, user.hashed_password):
            raise BadRequestException("Current password is incorrect")

        await self.user_repo.update(user_id, hashed_password=hash_password(new_password))
        return True

    async def get_current_user(self, user_id: uuid.UUID) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")
        return user

    async def _create_tokens(self, user: User) -> dict:
        token_data = {"sub": str(user.id), "role": user.role.value if hasattr(user.role, 'value') else user.role}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        await self.user_repo.update(user.id, refresh_token=refresh_token)
        return {"access_token": access_token, "refresh_token": refresh_token}

    @staticmethod
    def _generate_reset_token() -> str:
        return uuid.uuid4().hex
