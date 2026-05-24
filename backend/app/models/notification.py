from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import String, DateTime, Text, Boolean, ForeignKey, Enum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.models.base import Base, SoftDeleteMixin, TimestampMixin


class NotificationType(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    SUCCESS = "success"
    ERROR = "error"


class NotificationCategory(str, enum.Enum):
    ORDER = "order"
    SHIPMENT = "shipment"
    INVENTORY = "inventory"
    SYSTEM = "system"


class Notification(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "notifications"

    user_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
        index=True
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    type: Mapped[NotificationType] = mapped_column(
        Enum(NotificationType, values_callable=lambda enum_cls: [item.value for item in enum_cls]),
        default=NotificationType.INFO,
        nullable=False
    )
    category: Mapped[NotificationCategory] = mapped_column(
        Enum(NotificationCategory, values_callable=lambda enum_cls: [item.value for item in enum_cls]),
        default=NotificationCategory.SYSTEM,
        nullable=False
    )
    reference_type: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    reference_id: Mapped[Optional[UUID]] = mapped_column(nullable=True)
    is_read: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    read_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    action_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="user_notifications"
    )

    __table_args__ = (
        Index('ix_notifications_user_id_is_read', 'user_id', 'is_read'),
        Index('ix_notifications_created_at_desc', 'created_at'),
    )
