from fastapi import APIRouter
from app.api.v1 import auth, users, vendors, products, inventory, warehouses, orders, shipments, invoices, analytics, notifications, audit_logs, uploads

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(vendors.router)
api_router.include_router(products.router)
api_router.include_router(inventory.router)
api_router.include_router(warehouses.router)
api_router.include_router(orders.router)
api_router.include_router(shipments.router)
api_router.include_router(invoices.router)
api_router.include_router(analytics.router)
api_router.include_router(notifications.router)
api_router.include_router(audit_logs.router)
api_router.include_router(uploads.router)
