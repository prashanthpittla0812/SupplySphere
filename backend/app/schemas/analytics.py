from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_orders: int = 0
    total_revenue: float = 0.0
    total_products: int = 0
    total_vendors: int = 0
    total_shipments: int = 0
    pending_orders: int = 0
    low_stock_items: int = 0
    active_users: int = 0


class RevenueData(BaseModel):
    date: str
    revenue: float
    orders: int


class OrderStatusDistribution(BaseModel):
    status: str
    count: int


class CategoryBreakdown(BaseModel):
    category: str
    count: int
    total_value: float


class MonthlyTrend(BaseModel):
    month: str
    revenue: float
    orders: int


class TopProduct(BaseModel):
    product_id: UUID
    product_name: str
    total_quantity: float
    total_revenue: float


class RecentActivity(BaseModel):
    id: UUID
    action: str
    entity_type: str
    description: Optional[str] = None
    user_name: str
    timestamp: datetime
