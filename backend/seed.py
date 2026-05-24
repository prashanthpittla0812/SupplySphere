import asyncio
import uuid
from datetime import datetime, timedelta, timezone, date
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.vendor import Vendor
from app.models.product import Product
from app.models.warehouse import Warehouse
from app.models.inventory import Inventory
from app.models.order import PurchaseOrder, PurchaseOrderItem
from app.models.shipment import Shipment
from app.models.invoice import Invoice
from app.models.notification import Notification
from app.core.security import hash_password
import random


async def seed():
    async with AsyncSessionLocal() as db:
        try:
            from sqlalchemy import select, func

            demo_users = [
                ("admin@scm.com", "admin", "Admin@123", "System Administrator", "admin"),
                ("warehouse@scm.com", "warehouse_manager", "Warehouse@123", "Warehouse Manager", "warehouse_manager"),
                ("vendor@scm.com", "vendor", "Vendor@123", "Vendor Representative", "vendor"),
                ("delivery@scm.com", "delivery", "Delivery@123", "Delivery Personnel", "delivery_personnel"),
            ]
            users_data = []
            for email, username, password, full_name, role in demo_users:
                existing = await db.execute(select(User).where(User.email == email))
                user = existing.scalar_one_or_none()
                if user:
                    user.username = username
                    user.hashed_password = hash_password(password)
                    user.full_name = full_name
                    user.role = role
                    user.is_active = True
                    user.is_verified = True
                    user.is_deleted = False
                    user.deleted_at = None
                else:
                    user = User(
                        id=uuid.uuid4(),
                        email=email,
                        username=username,
                        hashed_password=hash_password(password),
                        full_name=full_name,
                        role=role,
                        is_active=True,
                        is_verified=True,
                    )
                    db.add(user)
                users_data.append(user)
            await db.flush()
            print("Demo users created or reset")

            result = await db.execute(select(func.count(Vendor.id)))
            count = result.scalar()
            if count > 0:
                await db.commit()
                print("Demo users reset. Existing business data was left unchanged.")
                print("\nDefault passwords:")
                print("  admin@scm.com     -> Admin@123")
                print("  warehouse@scm.com -> Warehouse@123")
                print("  vendor@scm.com    -> Vendor@123")
                print("  delivery@scm.com  -> Delivery@123")
                return

            vendors_data = [
                Vendor(id=uuid.uuid4(), name="TechPro Solutions", company_name="TechPro Solutions Pvt Ltd", email="contact@techpro.com", phone="+1-555-0101", address="123 Tech Park", city="San Francisco", state="CA", country="USA", pincode="94105", gst_number="GST-TP-001", status="active", contact_person="John Smith", created_by=users_data[0].id, rating=4.5, total_orders=15),
                Vendor(id=uuid.uuid4(), name="Global Trade Inc", company_name="Global Trade Inc", email="info@globaltrade.com", phone="+1-555-0102", address="456 Commerce St", city="New York", state="NY", country="USA", pincode="10001", gst_number="GST-GT-002", status="active", contact_person="Jane Doe", created_by=users_data[0].id, rating=4.2, total_orders=10),
                Vendor(id=uuid.uuid4(), name="Prime Suppliers", company_name="Prime Suppliers LLC", email="orders@primesupply.com", phone="+1-555-0103", address="789 Industrial Ave", city="Chicago", state="IL", country="USA", pincode="60601", gst_number="GST-PS-003", status="pending", contact_person="Bob Wilson", created_by=users_data[1].id, rating=0, total_orders=0),
            ]
            for v in vendors_data:
                db.add(v)
            await db.flush()
            print("Vendors created")

            warehouses_data = [
                Warehouse(id=uuid.uuid4(), name="Main Warehouse - East", code="WH-EAST-01", address="100 Logistics Blvd", city="Newark", state="NJ", country="USA", pincode="07101", capacity=50000.0, used_capacity=12500.0, status="active", manager_id=users_data[1].id, latitude=40.7357, longitude=-74.1724),
                Warehouse(id=uuid.uuid4(), name="West Coast DC", code="WH-WEST-01", address="200 Port Way", city="Oakland", state="CA", country="USA", pincode="94601", capacity=35000.0, used_capacity=8750.0, status="active", manager_id=users_data[1].id, latitude=37.8044, longitude=-122.2712),
                Warehouse(id=uuid.uuid4(), name="Central Hub", code="WH-CENT-01", address="300 Distribution Dr", city="Dallas", state="TX", country="USA", pincode="75201", capacity=25000.0, used_capacity=6200.0, status="active", manager_id=users_data[1].id, latitude=32.7767, longitude=-96.7970),
                Warehouse(id=uuid.uuid4(), name="South Region WH", code="WH-SOUTH-01", address="400 Storage Ave", city="Atlanta", state="GA", country="USA", pincode="30301", capacity=20000.0, used_capacity=5000.0, status="inactive", manager_id=users_data[1].id, latitude=33.7490, longitude=-84.3880),
            ]
            for w in warehouses_data:
                db.add(w)
            await db.flush()
            print("Warehouses created")

            categories = ["Electronics", "Office Supplies", "Industrial Equipment", "Packaging Materials", "Safety Equipment"]
            product_names = [
                ("Laptop Pro X1", "LPT-PRO-X1", 1299.99, 850.00),
                ("Wireless Mouse M3", "MOU-WL-M3", 49.99, 25.00),
                ("Mechanical Keyboard K1", "KEY-MECH-K1", 89.99, 45.00),
                ('27" 4K Monitor', "MON-4K-27", 499.99, 300.00),
                ("Industrial Printer P100", "PRN-IND-P100", 2499.99, 1800.00),
                ("Warehouse Scanner Gun", "SCN-GUN-WH", 299.99, 175.00),
                ("Safety Hard Hat", "SF-HAT-V2", 19.99, 8.00),
                ("Packing Tape (Case)", "TAPE-PAK-CS", 29.99, 15.00),
                ("Corrugated Box L", "BOX-COR-LG", 1.99, 0.80),
                ("Forklift Battery", "FL-BAT-48V", 899.99, 600.00),
                ("Pallet Jack Standard", "PAL-JCK-SD", 349.99, 200.00),
                ("LED Work Light", "LED-WL-100", 59.99, 30.00),
            ]
            products_data = []
            for i, (name, sku, price, cost) in enumerate(product_names):
                product = Product(id=uuid.uuid4(), name=name, sku=sku, description=f"{name} - Enterprise grade", category=categories[i % len(categories)], unit_price=price, unit_cost=cost, tax_rate=8.5, unit="pcs", min_stock_level=10.0 if i < 4 else 5.0, vendor_id=vendors_data[i % 2].id, is_active=True)
                products_data.append(product)
                db.add(product)
            await db.flush()
            print("Products created")

            inventory_data = []
            for i, product in enumerate(products_data):
                for j, warehouse in enumerate(warehouses_data[:3]):
                    quantity = random.randint(50, 500)
                    inv = Inventory(id=uuid.uuid4(), product_id=product.id, warehouse_id=warehouse.id, quantity=float(quantity), reserved_quantity=float(random.randint(0, int(quantity * 0.2))))
                    inventory_data.append(inv)
                    db.add(inv)
            await db.flush()
            print("Inventory created")

            orders_data = []
            order_numbers = ["PO-2024-0001", "PO-2024-0002", "PO-2024-0003", "PO-2024-0004", "PO-2024-0005"]
            statuses = ["pending", "approved", "shipped", "delivered", "cancelled"]
            priority = ["medium", "high", "low", "urgent", "medium"]
            for i in range(5):
                vendor = vendors_data[i % 2]
                warehouse = warehouses_data[i % 3]
                subtotal = random.uniform(1000, 15000)
                tax = subtotal * 0.085
                total = subtotal + tax
                order = PurchaseOrder(
                    id=uuid.uuid4(),
                    order_number=order_numbers[i],
                    vendor_id=vendor.id,
                    warehouse_id=warehouse.id,
                    status=statuses[i],
                    priority=priority[i],
                    subtotal=round(subtotal, 2),
                    tax_amount=round(tax, 2),
                    discount=0.0,
                    total_amount=round(total, 2),
                    currency="USD",
                    notes=f"Order {order_numbers[i]} notes",
                    terms="Net 30",
                    ordered_by=users_data[0].id,
                    approved_by=users_data[0].id if i >= 1 else None,
                    approved_at=datetime.now(timezone.utc) - timedelta(days=i) if i >= 1 else None,
                    expected_delivery_date=date.today() + timedelta(days=7 * (i + 1)),
                    delivered_date=date.today() - timedelta(days=i) if i >= 3 else None,
                )
                orders_data.append(order)
                db.add(order)
            await db.flush()

            for i, order in enumerate(orders_data):
                for j in range(random.randint(2, 5)):
                    product = random.choice(products_data)
                    qty = random.randint(5, 50)
                    item = PurchaseOrderItem(
                        id=uuid.uuid4(),
                        order_id=order.id,
                        product_id=product.id,
                        quantity=float(qty),
                        unit_price=product.unit_price,
                        total_price=round(product.unit_price * qty, 2),
                        received_quantity=float(qty) if order.status == "delivered" else 0.0,
                        status="received" if order.status == "delivered" else "pending",
                    )
                    db.add(item)
            await db.flush()
            print("Orders created")

            shipments_data = [
                Shipment(id=uuid.uuid4(), tracking_number="SHP-2024-A1B2C3", order_id=orders_data[2].id, carrier="FedEx", status="in_transit", origin_warehouse_id=warehouses_data[0].id, destination_address="123 Tech Park, San Francisco, CA 94105", estimated_delivery=datetime.now(timezone.utc) + timedelta(days=2), shipped_date=datetime.now(timezone.utc) - timedelta(days=1), shipped_by=users_data[1].id, weight=45.5, dimensions="24x18x12", notes="Handle with care", current_location="Chicago, IL"),
                Shipment(id=uuid.uuid4(), tracking_number="SHP-2024-D4E5F6", order_id=orders_data[3].id, carrier="UPS", status="delivered", origin_warehouse_id=warehouses_data[1].id, destination_address="456 Commerce St, New York, NY 10001", estimated_delivery=datetime.now(timezone.utc) - timedelta(days=1), actual_delivery=datetime.now(timezone.utc) - timedelta(days=2), shipped_date=datetime.now(timezone.utc) - timedelta(days=5), shipped_by=users_data[1].id, weight=120.0, dimensions="36x24x24", notes="Fragile items inside"),
                Shipment(id=uuid.uuid4(), tracking_number="SHP-2024-G7H8I9", order_id=orders_data[0].id, carrier="DHL", status="pending", origin_warehouse_id=warehouses_data[2].id, destination_address="789 Industrial Ave, Chicago, IL 60601", estimated_delivery=datetime.now(timezone.utc) + timedelta(days=5), weight=78.3, dimensions="30x20x18"),
            ]
            for s in shipments_data:
                db.add(s)
            await db.flush()
            print("Shipments created")

            invoices_data = [
                Invoice(id=uuid.uuid4(), invoice_number="INV-2024-001", order_id=orders_data[3].id, vendor_id=orders_data[3].vendor_id, status="paid", issue_date=date.today() - timedelta(days=10), due_date=date.today() - timedelta(days=5), paid_date=date.today() - timedelta(days=3), subtotal=5000.00, tax_amount=425.00, discount=50.00, total_amount=5375.00, amount_paid=5375.00, balance_due=0.0, notes="Paid in full", created_by=users_data[0].id),
                Invoice(id=uuid.uuid4(), invoice_number="INV-2024-002", order_id=orders_data[2].id, vendor_id=orders_data[2].vendor_id, status="sent", issue_date=date.today() - timedelta(days=5), due_date=date.today() + timedelta(days=25), subtotal=3200.00, tax_amount=272.00, discount=0.0, total_amount=3472.00, amount_paid=0.0, balance_due=3472.00, notes="Net 30 terms", created_by=users_data[0].id),
                Invoice(id=uuid.uuid4(), invoice_number="INV-2024-003", order_id=orders_data[0].id, vendor_id=orders_data[0].vendor_id, status="draft", issue_date=date.today(), due_date=date.today() + timedelta(days=30), subtotal=8500.00, tax_amount=722.50, discount=100.00, total_amount=9122.50, amount_paid=0.0, balance_due=9122.50, notes="Pending review", created_by=users_data[0].id),
            ]
            for inv in invoices_data:
                db.add(inv)
            await db.flush()
            print("Invoices created")

            notifications_data = [
                Notification(id=uuid.uuid4(), user_id=users_data[0].id, title="New Vendor Registration", message="Prime Suppliers LLC has registered and is pending approval", type="info", category="system", is_read=False, action_url="/vendors"),
                Notification(id=uuid.uuid4(), user_id=users_data[1].id, title="Low Stock Alert", message="Laptop Pro X1 is below minimum stock level", type="warning", category="inventory", is_read=False, action_url="/inventory"),
                Notification(id=uuid.uuid4(), user_id=users_data[0].id, title="Order Approved", message="Purchase Order PO-2024-0002 has been approved", type="success", category="order", is_read=True, read_at=datetime.now(timezone.utc) - timedelta(hours=2), action_url="/orders/PO-2024-0002"),
                Notification(id=uuid.uuid4(), title="Shipment In Transit", message="Shipment SHP-2024-A1B2C3 is now in transit", type="info", category="shipment", is_read=False, reference_type="shipment",                 reference_id=shipments_data[0].id),
                Notification(id=uuid.uuid4(), user_id=users_data[3].id, title="New Delivery Assignment", message="You have been assigned to deliver shipment SHP-2024-A1B2C3", type="info", category="shipment", is_read=False, action_url="/shipments"),
            ]
            for n in notifications_data:
                db.add(n)
            await db.flush()
            print("Notifications created")

            await db.commit()
            print("\nDatabase seeded successfully!")
            print("\nUsers:")
            for u in users_data:
                print(f"  {u.email} / {u.full_name} (role: {u.role})")
            print("\nDefault passwords:")
            print("  admin@scm.com     -> Admin@123")
            print("  warehouse@scm.com -> Warehouse@123")
            print("  vendor@scm.com    -> Vendor@123")
            print("  delivery@scm.com  -> Delivery@123")

        except Exception as e:
            await db.rollback()
            print(f"Error seeding database: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(seed())
