from datetime import date, datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Date, DateTime, Enum, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.models.base import Base, SoftDeleteMixin, TimestampMixin


class ShipmentStatus(str, enum.Enum):
    PENDING = "pending"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Shipment(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "shipments"

    tracking_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    order_id: Mapped[UUID] = mapped_column(ForeignKey("purchase_orders.id"), nullable=False, index=True)
    order_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    carrier: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[ShipmentStatus] = mapped_column(
        Enum(ShipmentStatus, values_callable=lambda enum_cls: [item.value for item in enum_cls]),
        default=ShipmentStatus.PENDING,
        nullable=False,
        index=True,
    )
    origin_warehouse_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("warehouses.id"), nullable=True, index=True)
    warehouse_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    destination_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    estimated_delivery: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    actual_delivery: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    shipped_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    shipped_by: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    shipped_by_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    weight: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    dimensions: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    current_location: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_updated: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    order: Mapped["PurchaseOrder"] = relationship("PurchaseOrder", back_populates="shipments")
    origin_warehouse: Mapped[Optional["Warehouse"]] = relationship("Warehouse")
