"""Seed runner — imports and orchestrates all seed sections."""

import sys
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, sync_engine
from app.core.security import hash_password
from app.models import (
    Base,
    Role,
    User,
    Vendor,
    Warehouse,
    Product,
    Inventory,
    PurchaseOrder,
    PurchaseOrderItem,
    Shipment,
    Invoice,
    Notification,
)
from app.db.seeds.seed_data import (
    ROLES_DATA,
    DEMO_USERS,
    _user_id_by_email,
    VENDORS_DATA,
    WAREHOUSES_DATA,
    PRODUCT_DEFS,
    build_products,
    build_inventory,
    build_orders,
    build_shipments,
    build_invoices,
    build_notifications,
)
from app.db.seeds import SeedLogger, _table_is_empty


# ---------------------------------------------------------------------------
# Seed sections  (each is idempotent — skips if data exists)
# ---------------------------------------------------------------------------
async def seed_roles(db: AsyncSession, log: SeedLogger):
    if not await _table_is_empty(db, Role):
        log.skip("Roles table already populated")
        return
    for data in ROLES_DATA:
        db.add(Role(**data))
    await db.flush()
    log.ok(f"Seeded {len(ROLES_DATA)} roles")


async def seed_users(db: AsyncSession, log: SeedLogger):
    seeded = 0
    for uid, email, username, plain_pw, full_name, role, is_active, is_verified in DEMO_USERS:
        existing = await db.execute(select(User).where(User.email == email))
        user = existing.scalar_one_or_none()
        if user:
            user.username = username
            user.hashed_password = hash_password(plain_pw)
            user.full_name = full_name
            user.role = role
            user.is_active = is_active
            user.is_verified = is_verified
            user.is_deleted = False
            user.deleted_at = None
            log.info(f"Updated user: {email}")
        else:
            user = User(
                id=uid,
                email=email,
                username=username,
                hashed_password=hash_password(plain_pw),
                full_name=full_name,
                role=role,
                is_active=is_active,
                is_verified=is_verified,
            )
            db.add(user)
            seeded += 1
    await db.flush()
    log.ok(f"Seeded / updated {len(DEMO_USERS)} users ({seeded} new)")


async def seed_vendors(db: AsyncSession, log: SeedLogger):
    if not await _table_is_empty(db, Vendor):
        log.skip("Vendors table already populated")
        return
    for data in VENDORS_DATA:
        db.add(Vendor(**data))
    await db.flush()
    log.ok(f"Seeded {len(VENDORS_DATA)} vendors")


async def seed_warehouses(db: AsyncSession, log: SeedLogger):
    if not await _table_is_empty(db, Warehouse):
        log.skip("Warehouses table already populated")
        return
    for data in WAREHOUSES_DATA:
        db.add(Warehouse(**data))
    await db.flush()
    log.ok(f"Seeded {len(WAREHOUSES_DATA)} warehouses")


async def seed_products(db: AsyncSession, log: SeedLogger):
    if not await _table_is_empty(db, Product):
        log.skip("Products table already populated")
        return
    vendor_result = await db.execute(select(Vendor.id))
    vendor_ids = vendor_result.scalars().all()
    products = build_products(list(vendor_ids))
    for data in products:
        db.add(Product(**data))
    await db.flush()
    log.ok(f"Seeded {len(products)} products")


async def seed_inventory(db: AsyncSession, log: SeedLogger):
    if not await _table_is_empty(db, Inventory):
        log.skip("Inventory table already populated")
        return
    prod_result = await db.execute(select(Product.id))
    product_ids = prod_result.scalars().all()
    wh_result = await db.execute(select(Warehouse.id))
    warehouse_ids = wh_result.scalars().all()
    records = build_inventory(list(product_ids), list(warehouse_ids))
    for data in records:
        db.add(Inventory(**data))
    await db.flush()
    log.ok(f"Seeded {len(records)} inventory records")


async def seed_orders(db: AsyncSession, log: SeedLogger):
    if not await _table_is_empty(db, PurchaseOrder):
        log.skip("Orders table already populated")
        return
    vendor_ids = (await db.execute(select(Vendor.id))).scalars().all()
    warehouse_ids = (await db.execute(select(Warehouse.id))).scalars().all()
    product_ids = (await db.execute(select(Product.id))).scalars().all()
    admin_id = _user_id_by_email("admin@supplysphere.com")
    wh_mgr_id = _user_id_by_email("warehouse@supplysphere.com")

    orders, items = build_orders(
        list(vendor_ids), list(warehouse_ids), list(product_ids), PRODUCT_DEFS, admin_id, wh_mgr_id
    )
    for data in orders:
        db.add(PurchaseOrder(**data))
    await db.flush()
    for data in items:
        db.add(PurchaseOrderItem(**data))
    await db.flush()
    log.ok(f"Seeded {len(orders)} orders with {len(items)} items")


async def seed_shipments(db: AsyncSession, log: SeedLogger):
    if not await _table_is_empty(db, Shipment):
        log.skip("Shipments table already populated")
        return
    order_ids = (await db.execute(select(PurchaseOrder.id))).scalars().all()
    warehouse_ids = (await db.execute(select(Warehouse.id))).scalars().all()
    wh_mgr_id = _user_id_by_email("warehouse@supplysphere.com")

    shipments = build_shipments(list(order_ids), list(warehouse_ids), wh_mgr_id)
    for data in shipments:
        db.add(Shipment(**data))
    await db.flush()
    log.ok(f"Seeded {len(shipments)} shipments")


async def seed_invoices(db: AsyncSession, log: SeedLogger):
    if not await _table_is_empty(db, Invoice):
        log.skip("Invoices table already populated")
        return
    order_ids = (await db.execute(select(PurchaseOrder.id))).scalars().all()
    vendor_ids = (await db.execute(select(Vendor.id))).scalars().all()
    admin_id = _user_id_by_email("admin@supplysphere.com")

    invoices = build_invoices(list(order_ids), list(vendor_ids), admin_id)
    for data in invoices:
        db.add(Invoice(**data))
    await db.flush()
    log.ok(f"Seeded {len(invoices)} invoices")


async def seed_notifications(db: AsyncSession, log: SeedLogger):
    if not await _table_is_empty(db, Notification):
        log.skip("Notifications table already populated")
        return
    shipment_ids = (await db.execute(select(Shipment.id))).scalars().all()
    shipments = [{"id": sid} for sid in shipment_ids]

    notifs = build_notifications(None, shipments)
    for data in notifs:
        db.add(Notification(**data))
    await db.flush()
    log.ok(f"Seeded {len(notifs)} notifications")


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------
SEED_ORDER = [
    ("Roles",        seed_roles),
    ("Users",        seed_users),
    ("Vendors",      seed_vendors),
    ("Warehouses",   seed_warehouses),
    ("Products",     seed_products),
    ("Inventory",    seed_inventory),
    ("Orders",       seed_orders),
    ("Shipments",    seed_shipments),
    ("Invoices",     seed_invoices),
    ("Notifications", seed_notifications),
]


def create_tables():
    """Create all database tables if they don't already exist."""
    Base.metadata.create_all(sync_engine)


async def seed_database(db: AsyncSession, log: SeedLogger):
    """Execute all seed sections in dependency order."""
    create_tables()
    for name, fn in SEED_ORDER:
        try:
            await fn(db, log)
        except Exception as e:
            log.info(f"ERROR seeding {name}: {e}")
            raise
    await db.commit()


async def seed_all(users_only: bool = False, silent: bool = False):
    """Top-level seed entry point.

    Parameters
    ----------
    users_only : bool
        If True, only seed/update the demo users.
    silent : bool
        If True, suppress all log output.
    """
    log = SeedLogger(silent=silent)

    create_tables()

    async with AsyncSessionLocal() as db:
        try:
            if users_only:
                await seed_users(db, log)
                await db.commit()
                log.ok("Users updated successfully")
                return

            await seed_database(db, log)

            print()
            print("=" * 55)
            print("  SupplySphere Demo Database Seeded Successfully")
            print("=" * 55)
            print()
            print("  Login Credentials:")
            print("  " + "-" * 50)
            for _, email, _, plain_pw, full_name, role, *_ in DEMO_USERS:
                print(f"    {email}")
                print(f"    Password: {plain_pw}")
                print(f"    Role:     {role}")
                print()
            print("=" * 55)

        except Exception as e:
            await db.rollback()
            print(f"\n  [ERROR] Seeding failed: {e}", file=sys.stderr)
            raise


async def auto_seed_if_empty():
    """Called on app startup — seeds only when users table is empty.

    Ensures tables exist before checking emptiness so fresh databases
    (e.g. Neon PostgreSQL on first deploy) do not crash with a
    'relation does not exist' error.
    """
    try:
        create_tables()
    except Exception as e:
        print(f"[AUTO-SEED] Could not create tables: {e}")
        return

    async with AsyncSessionLocal() as db:
        try:
            if await _table_is_empty(db, User):
                print("[AUTO-SEED] Database is empty. Running initial seed...")
                await seed_database(db, SeedLogger(silent=False))
                print("[AUTO-SEED] Initial seed complete.")
            else:
                print("[AUTO-SEED] Database already populated \u2014 skipping.")
        except Exception as e:
            await db.rollback()
            print(f"[AUTO-SEED] Seeding failed: {e}", file=sys.stderr)
