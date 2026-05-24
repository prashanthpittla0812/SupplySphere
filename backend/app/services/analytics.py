from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.user import User
from app.models.vendor import Vendor
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.order import PurchaseOrder
from app.models.shipment import Shipment
from app.models.invoice import Invoice
from app.models.audit_log import AuditLog
from app.models.notification import Notification
from app.repositories.user import UserRepository
from app.repositories.vendor import VendorRepository
from app.repositories.product import ProductRepository


class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.vendor_repo = VendorRepository(db)
        self.product_repo = ProductRepository(db)

    async def get_dashboard_stats(self) -> dict:
        total_orders_q = select(func.count(PurchaseOrder.id)).where(PurchaseOrder.is_deleted == False)
        total_revenue_q = select(func.coalesce(func.sum(Invoice.amount_paid), 0)).where(
            Invoice.is_deleted == False, Invoice.status == "paid"
        )
        total_products_q = select(func.count(Product.id)).where(Product.is_deleted == False)
        total_vendors_q = select(func.count(Vendor.id)).where(Vendor.is_deleted == False)
        total_shipments_q = select(func.count(Shipment.id)).where(Shipment.is_deleted == False)
        pending_orders_q = select(func.count(PurchaseOrder.id)).where(
            PurchaseOrder.is_deleted == False, PurchaseOrder.status == "pending"
        )
        low_stock_q = (
            select(func.count(Inventory.product_id.distinct()))
            .join(Product, Inventory.product_id == Product.id)
            .where(
                Inventory.is_deleted == False,
                Product.is_deleted == False,
                Inventory.quantity < Product.min_stock_level,
            )
        )
        active_users_q = select(func.count(User.id)).where(User.is_deleted == False, User.is_active == True)

        results = await self.db.execute(total_orders_q)
        total_orders = results.scalar() or 0

        results = await self.db.execute(total_revenue_q)
        total_revenue = float(results.scalar() or 0)

        results = await self.db.execute(total_products_q)
        total_products = results.scalar() or 0

        results = await self.db.execute(total_vendors_q)
        total_vendors = results.scalar() or 0

        results = await self.db.execute(total_shipments_q)
        total_shipments = results.scalar() or 0

        results = await self.db.execute(pending_orders_q)
        pending_orders = results.scalar() or 0

        results = await self.db.execute(low_stock_q)
        low_stock_items = results.scalar() or 0

        results = await self.db.execute(active_users_q)
        active_users = results.scalar() or 0

        return {
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "total_products": total_products,
            "total_vendors": total_vendors,
            "total_shipments": total_shipments,
            "pending_orders": pending_orders,
            "low_stock_items": low_stock_items,
            "active_users": active_users,
        }

    async def get_revenue_chart(self, days: int = 30, period: str = None, year: int = None) -> list:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        query = select(
            func.date(Invoice.paid_date).label("date"),
            func.coalesce(func.sum(Invoice.amount_paid), 0).label("revenue"),
        ).where(
            Invoice.is_deleted == False,
            Invoice.status == "paid",
            Invoice.paid_date >= cutoff,
        ).group_by(func.date(Invoice.paid_date)).order_by(func.date(Invoice.paid_date))
        result = await self.db.execute(query)
        rows = result.all()
        return [{"date": str(row.date), "revenue": float(row.revenue)} for row in rows]

    async def get_order_status_distribution(self) -> list:
        query = select(
            PurchaseOrder.status,
            func.count(PurchaseOrder.id).label("count"),
        ).where(PurchaseOrder.is_deleted == False).group_by(PurchaseOrder.status)
        result = await self.db.execute(query)
        rows = result.all()
        return [{"status": row.status, "count": row.count} for row in rows]

    async def get_category_breakdown(self) -> list:
        return await self.product_repo.get_category_breakdown()

    async def get_monthly_trends(self, months: int = 12, year: int = None) -> list:
        from sqlalchemy import extract
        cutoff = datetime.now(timezone.utc) - timedelta(days=30 * months)
        query = select(
            extract('year', PurchaseOrder.created_at).label("year"),
            extract('month', PurchaseOrder.created_at).label("month"),
            func.count(PurchaseOrder.id).label("count"),
            func.coalesce(func.sum(PurchaseOrder.total_amount), 0).label("revenue"),
        ).where(
            PurchaseOrder.is_deleted == False,
            PurchaseOrder.created_at >= cutoff,
        ).group_by("year", "month").order_by("year", "month")
        result = await self.db.execute(query)
        rows = result.all()
        return [
            {"year": int(row.year), "month": int(row.month), "count": row.count, "revenue": float(row.revenue)}
            for row in rows
        ]

    async def get_top_products(self, limit: int = 10) -> list:
        query = (
            select(
                Product.id,
                Product.name,
                Product.sku,
                func.coalesce(func.sum(Inventory.quantity), 0).label("total_stock"),
            )
            .join(Inventory, Product.id == Inventory.product_id, isouter=True)
            .where(Product.is_deleted == False, Inventory.is_deleted == False)
            .group_by(Product.id)
            .order_by(func.coalesce(func.sum(Inventory.quantity), 0).desc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        rows = result.all()
        return [
            {"id": str(row.id), "name": row.name, "sku": row.sku, "total_stock": float(row.total_stock)}
            for row in rows
        ]

    async def get_recent_activity(self, limit: int = 20) -> list:
        query = (
            select(AuditLog)
            .where(AuditLog.is_deleted == False)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        logs = result.scalars().all()
        return [
            {
                "id": str(log.id),
                "user_id": str(log.user_id) if log.user_id else None,
                "action": log.action,
                "entity_type": log.entity_type,
                "description": log.description,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ]
