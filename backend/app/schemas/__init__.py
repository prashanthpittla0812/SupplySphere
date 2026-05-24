from app.schemas.analytics import (
    CategoryBreakdown,
    DashboardStats,
    MonthlyTrend,
    OrderStatusDistribution,
    RecentActivity,
    RevenueData,
    TopProduct,
)
from app.schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
)
from app.schemas.common import (
    APIResponse,
    ErrorResponse,
    PaginationMeta,
    PaginationParams,
)
from app.schemas.inventory import (
    InventoryBase,
    InventoryCreate,
    InventoryOut,
    InventoryUpdate,
    LowStockAlert,
    StockAdjustRequest,
)
from app.schemas.invoice import (
    InvoiceCreate,
    InvoiceOut,
    InvoicePayment,
    InvoiceUpdate,
)
from app.schemas.notification import (
    NotificationList,
    NotificationOut,
)
from app.schemas.order import (
    OrderApproval,
    OrderCreate,
    OrderItemCreate,
    OrderItemOut,
    OrderOut,
    OrderUpdate,
)
from app.schemas.product import (
    ProductBase,
    ProductCreate,
    ProductOut,
    ProductUpdate,
)
from app.schemas.shipment import (
    ShipmentCreate,
    ShipmentOut,
    ShipmentUpdate,
)
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserList,
    UserOut,
    UserUpdate,
)
from app.schemas.vendor import (
    VendorBase,
    VendorCreate,
    VendorOut,
    VendorUpdate,
)
from app.schemas.warehouse import (
    WarehouseBase,
    WarehouseCreate,
    WarehouseOut,
    WarehouseUpdate,
)

__all__ = [
    # common
    "PaginationParams",
    "PaginationMeta",
    "APIResponse",
    "ErrorResponse",
    # auth
    "RegisterRequest",
    "LoginRequest",
    "TokenResponse",
    "RefreshTokenRequest",
    "ForgotPasswordRequest",
    "ResetPasswordRequest",
    "ChangePasswordRequest",
    # user
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserOut",
    "UserList",
    # vendor
    "VendorBase",
    "VendorCreate",
    "VendorUpdate",
    "VendorOut",
    # product
    "ProductBase",
    "ProductCreate",
    "ProductUpdate",
    "ProductOut",
    # inventory
    "InventoryBase",
    "InventoryCreate",
    "InventoryUpdate",
    "InventoryOut",
    "LowStockAlert",
    "StockAdjustRequest",
    # warehouse
    "WarehouseBase",
    "WarehouseCreate",
    "WarehouseUpdate",
    "WarehouseOut",
    # order
    "OrderItemCreate",
    "OrderItemOut",
    "OrderCreate",
    "OrderUpdate",
    "OrderApproval",
    "OrderOut",
    # shipment
    "ShipmentCreate",
    "ShipmentUpdate",
    "ShipmentOut",
    # invoice
    "InvoiceCreate",
    "InvoiceUpdate",
    "InvoicePayment",
    "InvoiceOut",
    # notification
    "NotificationOut",
    "NotificationList",
    # analytics
    "DashboardStats",
    "RevenueData",
    "OrderStatusDistribution",
    "CategoryBreakdown",
    "MonthlyTrend",
    "TopProduct",
    "RecentActivity",
]
