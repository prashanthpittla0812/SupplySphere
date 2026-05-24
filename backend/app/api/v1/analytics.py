from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_session
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.common import APIResponse
from app.services.analytics import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    service = AnalyticsService(db)
    data = await service.get_dashboard_stats()
    data = {
        **data,
        "totalRevenue": data.get("total_revenue", 0),
        "revenueChange": 0,
        "totalOrders": data.get("total_orders", 0),
        "ordersChange": 0,
        "activeShipments": data.get("total_shipments", 0),
        "shipmentsChange": 0,
        "lowStockItems": data.get("low_stock_items", 0),
        "stockChange": 0,
    }
    return APIResponse(success=True, message="Dashboard stats retrieved successfully", data=data)


@router.get("/revenue")
async def get_revenue_chart(
    period: str = Query("monthly"),
    year: int = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    service = AnalyticsService(db)
    data = await service.get_revenue_chart(period=period, year=year)
    data = [
        {
            **item,
            "month": item.get("date", "")[-5:] or item.get("month", ""),
        }
        for item in data
    ]
    return APIResponse(success=True, message="Revenue chart data retrieved successfully", data=data)


@router.get("/orders/status-distribution")
async def get_order_status_distribution(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    service = AnalyticsService(db)
    data = await service.get_order_status_distribution()
    data = [
        {
            **item,
            "name": str(item.get("status", "")).replace("_", " ").title(),
            "value": item.get("count", 0),
        }
        for item in data
    ]
    return APIResponse(success=True, message="Order status distribution retrieved successfully", data=data)


@router.get("/order-status")
async def get_order_status_distribution_legacy(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    return await get_order_status_distribution(current_user=current_user, db=db)


@router.get("/products/category-breakdown")
async def get_category_breakdown(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    service = AnalyticsService(db)
    data = await service.get_category_breakdown()
    return APIResponse(success=True, message="Category breakdown retrieved successfully", data=data)


@router.get("/inventory-by-category")
async def get_category_breakdown_legacy(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    return await get_category_breakdown(current_user=current_user, db=db)


@router.get("/trends/monthly")
async def get_monthly_trends(
    year: int = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    service = AnalyticsService(db)
    data = await service.get_monthly_trends(year=year)
    return APIResponse(success=True, message="Monthly trends retrieved successfully", data=data)


@router.get("/products/top")
async def get_top_products(
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    service = AnalyticsService(db)
    data = await service.get_top_products(limit=limit)
    return APIResponse(success=True, message="Top products retrieved successfully", data=data)


@router.get("/activity/recent")
async def get_recent_activity(
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    service = AnalyticsService(db)
    data = await service.get_recent_activity(limit=limit)
    return APIResponse(success=True, message="Recent activity retrieved successfully", data=data)
