"""SupplySphere Demo Seed Data.

All production credentials for demo and testing purposes only.
"""

from datetime import datetime, timedelta, timezone, date
from uuid import UUID, uuid4

# ---------------------------------------------------------------------------
# Roles
# ---------------------------------------------------------------------------
ROLES_DATA = [
    {"name": "admin", "description": "System administrator with full access", "is_system": True},
    {"name": "warehouse_manager", "description": "Manages warehouse operations and inventory", "is_system": True},
    {"name": "vendor", "description": "External vendor/supplier", "is_system": True},
    {"name": "delivery_personnel", "description": "Handles shipment delivery", "is_system": True},
]

# ---------------------------------------------------------------------------
# Demo users  — passwords are hashed at seed time with bcrypt
# ---------------------------------------------------------------------------
# Each entry: (id, email, username, plain_password, full_name, role, is_active, is_verified)
DEMO_USERS = [
    (uuid4(), "admin@supplysphere.com", "admin",           "Admin@123",      "System Administrator",  "admin",               True, True),
    (uuid4(), "warehouse@supplysphere.com", "warehouse_manager", "Warehouse@123", "Warehouse Manager",     "warehouse_manager",   True, True),
    (uuid4(), "vendor@supplysphere.com",    "vendor",          "Vendor@123",     "Vendor Representative", "vendor",              True, True),
    (uuid4(), "delivery@supplysphere.com",  "delivery",        "Delivery@123",   "Delivery Personnel",    "delivery_personnel",  True, True),
]

# Map email -> id so other seed data can reference users by email
def _user_id_by_email(email: str) -> UUID:
    for uid, em, *_ in DEMO_USERS:
        if em == email:
            return uid
    raise ValueError(f"Unknown user email: {email}")

# ---------------------------------------------------------------------------
# Vendors
# ---------------------------------------------------------------------------
VENDORS_DATA = [
    {
        "id": uuid4(),
        "name": "TechPro Solutions",
        "company_name": "TechPro Solutions Pvt Ltd",
        "email": "contact@techpro.com",
        "phone": "+1-555-0101",
        "address": "123 Tech Park",
        "city": "San Francisco",
        "state": "CA",
        "country": "USA",
        "pincode": "94105",
        "gst_number": "GST-TP-001",
        "status": "active",
        "contact_person": "John Smith",
        "created_by": _user_id_by_email("admin@supplysphere.com"),
        "rating": 4.5,
        "total_orders": 15,
    },
    {
        "id": uuid4(),
        "name": "Global Trade Inc",
        "company_name": "Global Trade Inc",
        "email": "info@globaltrade.com",
        "phone": "+1-555-0102",
        "address": "456 Commerce St",
        "city": "New York",
        "state": "NY",
        "country": "USA",
        "pincode": "10001",
        "gst_number": "GST-GT-002",
        "status": "active",
        "contact_person": "Jane Doe",
        "created_by": _user_id_by_email("admin@supplysphere.com"),
        "rating": 4.2,
        "total_orders": 10,
    },
    {
        "id": uuid4(),
        "name": "Prime Suppliers",
        "company_name": "Prime Suppliers LLC",
        "email": "orders@primesupply.com",
        "phone": "+1-555-0103",
        "address": "789 Industrial Ave",
        "city": "Chicago",
        "state": "IL",
        "country": "USA",
        "pincode": "60601",
        "gst_number": "GST-PS-003",
        "status": "pending",
        "contact_person": "Bob Wilson",
        "created_by": _user_id_by_email("warehouse@supplysphere.com"),
        "rating": 0.0,
        "total_orders": 0,
    },
]

# ---------------------------------------------------------------------------
# Warehouses
# ---------------------------------------------------------------------------
WAREHOUSES_DATA = [
    {
        "id": uuid4(),
        "name": "Main Warehouse - East",
        "code": "WH-EAST-01",
        "address": "100 Logistics Blvd",
        "city": "Newark",
        "state": "NJ",
        "country": "USA",
        "pincode": "07101",
        "capacity": 50000.0,
        "used_capacity": 12500.0,
        "status": "active",
        "manager_id": _user_id_by_email("warehouse@supplysphere.com"),
        "latitude": 40.7357,
        "longitude": -74.1724,
    },
    {
        "id": uuid4(),
        "name": "West Coast DC",
        "code": "WH-WEST-01",
        "address": "200 Port Way",
        "city": "Oakland",
        "state": "CA",
        "country": "USA",
        "pincode": "94601",
        "capacity": 35000.0,
        "used_capacity": 8750.0,
        "status": "active",
        "manager_id": _user_id_by_email("warehouse@supplysphere.com"),
        "latitude": 37.8044,
        "longitude": -122.2712,
    },
    {
        "id": uuid4(),
        "name": "Central Hub",
        "code": "WH-CENT-01",
        "address": "300 Distribution Dr",
        "city": "Dallas",
        "state": "TX",
        "country": "USA",
        "pincode": "75201",
        "capacity": 25000.0,
        "used_capacity": 6200.0,
        "status": "active",
        "manager_id": _user_id_by_email("warehouse@supplysphere.com"),
        "latitude": 32.7767,
        "longitude": -96.7970,
    },
    {
        "id": uuid4(),
        "name": "South Region WH",
        "code": "WH-SOUTH-01",
        "address": "400 Storage Ave",
        "city": "Atlanta",
        "state": "GA",
        "country": "USA",
        "pincode": "30301",
        "capacity": 20000.0,
        "used_capacity": 5000.0,
        "status": "inactive",
        "manager_id": _user_id_by_email("warehouse@supplysphere.com"),
        "latitude": 33.7490,
        "longitude": -84.3880,
    },
]

# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------
# (name, sku, unit_price, unit_cost, category, min_stock)
PRODUCT_DEFS = [
    ("Laptop Pro X1",         "LPT-PRO-X1",   1299.99,  850.00, "Electronics",          10.0),
    ("Wireless Mouse M3",     "MOU-WL-M3",      49.99,   25.00, "Electronics",          25.0),
    ("Mechanical Keyboard K1","KEY-MECH-K1",    89.99,   45.00, "Electronics",          20.0),
    ('27" 4K Monitor',        "MON-4K-27",     499.99,  300.00, "Electronics",          10.0),
    ("Industrial Printer P100","PRN-IND-P100", 2499.99, 1800.00, "Industrial Equipment",  5.0),
    ("Warehouse Scanner Gun", "SCN-GUN-WH",    299.99,  175.00, "Industrial Equipment", 10.0),
    ("Safety Hard Hat",       "SF-HAT-V2",      19.99,    8.00, "Safety Equipment",     50.0),
    ("Packing Tape (Case)",   "TAPE-PAK-CS",    29.99,   15.00, "Packaging Materials",  30.0),
    ("Corrugated Box L",      "BOX-COR-LG",      1.99,    0.80, "Packaging Materials", 200.0),
    ("Forklift Battery",      "FL-BAT-48V",    899.99,  600.00, "Industrial Equipment",  5.0),
    ("Pallet Jack Standard",  "PAL-JCK-SD",    349.99,  200.00, "Industrial Equipment",  8.0),
    ("LED Work Light",        "LED-WL-100",     59.99,   30.00, "Safety Equipment",     15.0),
]

CATEGORIES = ["Electronics", "Office Supplies", "Industrial Equipment", "Packaging Materials", "Safety Equipment"]

def build_products(vendor_ids: list[UUID]) -> list[dict]:
    products = []
    for i, (name, sku, price, cost, cat, min_stock) in enumerate(PRODUCT_DEFS):
        products.append({
            "id": uuid4(),
            "name": name,
            "sku": sku,
            "description": f"{name} - Enterprise grade",
            "category": cat,
            "unit_price": price,
            "unit_cost": cost,
            "tax_rate": 8.5,
            "unit": "pcs",
            "min_stock_level": min_stock,
            "vendor_id": vendor_ids[i % 2],
            "is_active": True,
        })
    return products

# ---------------------------------------------------------------------------
# Inventory  (built per product × warehouse)
# ---------------------------------------------------------------------------
import random
random.seed(42)

def build_inventory(product_ids: list[UUID], warehouse_ids: list[UUID]) -> list[dict]:
    records = []
    for pid in product_ids:
        for wid in warehouse_ids[:3]:
            qty = random.randint(50, 500)
            reserved = random.randint(0, int(qty * 0.2))
            records.append({
                "id": uuid4(),
                "product_id": pid,
                "warehouse_id": wid,
                "quantity": float(qty),
                "reserved_quantity": float(reserved),
            })
    return records

# ---------------------------------------------------------------------------
# Purchase Orders  +  Order Items
# ---------------------------------------------------------------------------
ORDER_NUMBERS = ["PO-2024-0001", "PO-2024-0002", "PO-2024-0003", "PO-2024-0004", "PO-2024-0005"]
ORDER_STATUSES = ["pending", "approved", "shipped", "delivered", "cancelled"]
ORDER_PRIORITIES = ["medium", "high", "low", "urgent", "medium"]

_TODAY = date.today()
_NOW = datetime.now(timezone.utc)

def build_orders(
    vendor_ids: list[UUID],
    warehouse_ids: list[UUID],
    product_ids: list[UUID],
    product_defs: list[tuple],
    admin_id: UUID,
    warehouse_mgr_id: UUID,
):
    orders = []
    items = []
    price_map = {pid: price for pid, (_, _, price, *_) in zip(product_ids, product_defs * 2)}

    for i in range(5):
        oid = uuid4()
        subtotal = round(random.uniform(1000, 15000), 2)
        tax = round(subtotal * 0.085, 2)
        total = round(subtotal + tax, 2)

        orders.append({
            "id": oid,
            "order_number": ORDER_NUMBERS[i],
            "vendor_id": vendor_ids[i % 2],
            "warehouse_id": warehouse_ids[i % 3],
            "status": ORDER_STATUSES[i],
            "priority": ORDER_PRIORITIES[i],
            "subtotal": subtotal,
            "tax_amount": tax,
            "discount": 0.0,
            "total_amount": total,
            "currency": "USD",
            "notes": f"Order {ORDER_NUMBERS[i]} notes",
            "terms": "Net 30",
            "ordered_by": admin_id,
            "approved_by": admin_id if i >= 1 else None,
            "approved_at": _NOW - timedelta(days=i) if i >= 1 else None,
            "expected_delivery_date": _TODAY + timedelta(days=7 * (i + 1)),
            "delivered_date": _TODAY - timedelta(days=i) if i >= 3 else None,
            "is_urgent": i == 3,
        })

        for _ in range(random.randint(2, 5)):
            pid = random.choice(product_ids)
            qty = random.randint(5, 50)
            price = price_map[pid]
            items.append({
                "id": uuid4(),
                "order_id": oid,
                "product_id": pid,
                "quantity": float(qty),
                "unit_price": price,
                "total_price": round(price * qty, 2),
                "received_quantity": float(qty) if ORDER_STATUSES[i] == "delivered" else 0.0,
                "status": "received" if ORDER_STATUSES[i] == "delivered" else "pending",
            })

    return orders, items

# ---------------------------------------------------------------------------
# Shipments
# ---------------------------------------------------------------------------
def build_shipments(
    order_ids: list[UUID],
    warehouse_ids: list[UUID],
    warehouse_mgr_id: UUID,
):
    return [
        {
            "id": uuid4(),
            "tracking_number": "SHP-2024-A1B2C3",
            "order_id": order_ids[2],
            "carrier": "FedEx",
            "status": "in_transit",
            "origin_warehouse_id": warehouse_ids[0],
            "destination_address": "123 Tech Park, San Francisco, CA 94105",
            "estimated_delivery": _TODAY + timedelta(days=2),
            "shipped_date": _NOW - timedelta(days=1),
            "shipped_by": warehouse_mgr_id,
            "weight": 45.5,
            "dimensions": "24x18x12",
            "notes": "Handle with care",
            "current_location": "Chicago, IL",
        },
        {
            "id": uuid4(),
            "tracking_number": "SHP-2024-D4E5F6",
            "order_id": order_ids[3],
            "carrier": "UPS",
            "status": "delivered",
            "origin_warehouse_id": warehouse_ids[1],
            "destination_address": "456 Commerce St, New York, NY 10001",
            "estimated_delivery": _TODAY - timedelta(days=1),
            "actual_delivery": _NOW - timedelta(days=2),
            "shipped_date": _NOW - timedelta(days=5),
            "shipped_by": warehouse_mgr_id,
            "weight": 120.0,
            "dimensions": "36x24x24",
            "notes": "Fragile items inside",
        },
        {
            "id": uuid4(),
            "tracking_number": "SHP-2024-G7H8I9",
            "order_id": order_ids[0],
            "carrier": "DHL",
            "status": "pending",
            "origin_warehouse_id": warehouse_ids[2],
            "destination_address": "789 Industrial Ave, Chicago, IL 60601",
            "estimated_delivery": _TODAY + timedelta(days=5),
            "weight": 78.3,
            "dimensions": "30x20x18",
        },
    ]

# ---------------------------------------------------------------------------
# Invoices
# ---------------------------------------------------------------------------
def build_invoices(
    order_ids: list[UUID],
    vendor_ids: list[UUID],
    admin_id: UUID,
):
    return [
        {
            "id": uuid4(),
            "invoice_number": "INV-2024-001",
            "order_id": order_ids[3],
            "vendor_id": vendor_ids[1],
            "status": "paid",
            "issue_date": _TODAY - timedelta(days=10),
            "due_date": _TODAY - timedelta(days=5),
            "paid_date": _NOW - timedelta(days=3),
            "subtotal": 5000.00,
            "tax_amount": 425.00,
            "discount": 50.00,
            "total_amount": 5375.00,
            "amount_paid": 5375.00,
            "balance_due": 0.0,
            "notes": "Paid in full",
            "created_by": admin_id,
        },
        {
            "id": uuid4(),
            "invoice_number": "INV-2024-002",
            "order_id": order_ids[2],
            "vendor_id": vendor_ids[0],
            "status": "sent",
            "issue_date": _TODAY - timedelta(days=5),
            "due_date": _TODAY + timedelta(days=25),
            "subtotal": 3200.00,
            "tax_amount": 272.00,
            "discount": 0.0,
            "total_amount": 3472.00,
            "amount_paid": 0.0,
            "balance_due": 3472.00,
            "notes": "Net 30 terms",
            "created_by": admin_id,
        },
        {
            "id": uuid4(),
            "invoice_number": "INV-2024-003",
            "order_id": order_ids[0],
            "vendor_id": vendor_ids[0],
            "status": "draft",
            "issue_date": _TODAY,
            "due_date": _TODAY + timedelta(days=30),
            "subtotal": 8500.00,
            "tax_amount": 722.50,
            "discount": 100.00,
            "total_amount": 9122.50,
            "amount_paid": 0.0,
            "balance_due": 9122.50,
            "notes": "Pending review",
            "created_by": admin_id,
        },
    ]

# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------
def build_notifications(users, shipments):
    return [
        {
            "user_id": _user_id_by_email("admin@supplysphere.com"),
            "title": "New Vendor Registration",
            "message": "Prime Suppliers LLC has registered and is pending approval",
            "type": "info",
            "category": "system",
            "is_read": False,
            "action_url": "/vendors",
        },
        {
            "user_id": _user_id_by_email("warehouse@supplysphere.com"),
            "title": "Low Stock Alert",
            "message": "Laptop Pro X1 is below minimum stock level",
            "type": "warning",
            "category": "inventory",
            "is_read": False,
            "action_url": "/inventory",
        },
        {
            "user_id": _user_id_by_email("admin@supplysphere.com"),
            "title": "Order Approved",
            "message": "Purchase Order PO-2024-0002 has been approved",
            "type": "success",
            "category": "order",
            "is_read": True,
            "read_at": _NOW - timedelta(hours=2),
            "action_url": "/orders/PO-2024-0002",
        },
        {
            "title": "Shipment In Transit",
            "message": "Shipment SHP-2024-A1B2C3 is now in transit",
            "type": "info",
            "category": "shipment",
            "is_read": False,
            "reference_type": "shipment",
            "reference_id": shipments[0]["id"] if shipments else None,
        },
        {
            "user_id": _user_id_by_email("delivery@supplysphere.com"),
            "title": "New Delivery Assignment",
            "message": "You have been assigned to deliver shipment SHP-2024-A1B2C3",
            "type": "info",
            "category": "shipment",
            "is_read": False,
            "action_url": "/shipments",
        },
    ]
