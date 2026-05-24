"""Initial SupplySphere schema.

Revision ID: 20260524_0001
Revises:
Create Date: 2026-05-24
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260524_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _uuid_pk() -> sa.Column:
    return sa.Column("id", sa.Uuid(), primary_key=True, nullable=False, index=True)


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def _soft_delete() -> list[sa.Column]:
    return [
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false(), index=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    ]


def upgrade() -> None:
    op.create_table("roles", _uuid_pk(), sa.Column("name", sa.String(50), nullable=False), sa.Column("description", sa.Text()), sa.Column("is_system", sa.Boolean(), nullable=False, server_default=sa.true()), *_timestamps())
    op.create_index("ix_roles_name", "roles", ["name"], unique=True)

    op.create_table(
        "users",
        _uuid_pk(),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("username", sa.String(50), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(100), nullable=False),
        sa.Column("phone", sa.String(20)),
        sa.Column("role", sa.String(30), nullable=False, server_default="vendor"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("refresh_token", sa.Text()),
        sa.Column("reset_token", sa.String(100)),
        sa.Column("reset_token_expires", sa.DateTime(timezone=True)),
        *_timestamps(),
        *_soft_delete(),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    op.create_table(
        "vendors",
        _uuid_pk(),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("company_name", sa.String(200), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(20), nullable=False),
        sa.Column("address", sa.Text(), nullable=False),
        sa.Column("city", sa.String(100), nullable=False),
        sa.Column("state", sa.String(100), nullable=False),
        sa.Column("country", sa.String(100), nullable=False),
        sa.Column("pincode", sa.String(20), nullable=False),
        sa.Column("gst_number", sa.String(30)),
        sa.Column("pan_number", sa.String(20)),
        sa.Column("contact_person", sa.String(200)),
        sa.Column("status", sa.String(30), nullable=False, server_default="active"),
        sa.Column("rating", sa.Float()),
        sa.Column("total_orders", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("notes", sa.Text()),
        sa.Column("created_by", sa.Uuid(), sa.ForeignKey("users.id")),
        *_timestamps(),
        *_soft_delete(),
    )
    op.create_index("ix_vendors_email", "vendors", ["email"], unique=True)

    op.create_table(
        "warehouses",
        _uuid_pk(),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("code", sa.String(20), nullable=False),
        sa.Column("address", sa.Text(), nullable=False),
        sa.Column("city", sa.String(100), nullable=False),
        sa.Column("state", sa.String(100), nullable=False),
        sa.Column("country", sa.String(100), nullable=False),
        sa.Column("pincode", sa.String(20), nullable=False),
        sa.Column("capacity", sa.Float(), nullable=False),
        sa.Column("used_capacity", sa.Float(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(30), nullable=False, server_default="active"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("manager_id", sa.Uuid(), sa.ForeignKey("users.id")),
        sa.Column("manager_name", sa.String(100)),
        sa.Column("latitude", sa.Float()),
        sa.Column("longitude", sa.Float()),
        *_timestamps(),
        *_soft_delete(),
    )
    op.create_index("ix_warehouses_code", "warehouses", ["code"], unique=True)

    op.create_table(
        "products",
        _uuid_pk(),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("sku", sa.String(50), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("unit_price", sa.Float(), nullable=False),
        sa.Column("unit_cost", sa.Float(), nullable=False),
        sa.Column("tax_rate", sa.Float(), nullable=False, server_default="0"),
        sa.Column("hsn_code", sa.String(20)),
        sa.Column("gst_rate", sa.Float()),
        sa.Column("unit", sa.String(50), nullable=False),
        sa.Column("min_stock_level", sa.Float(), nullable=False, server_default="0"),
        sa.Column("image_url", sa.Text()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("vendor_id", sa.Uuid(), sa.ForeignKey("vendors.id"), nullable=False),
        *_timestamps(),
        *_soft_delete(),
    )
    op.create_index("ix_products_sku", "products", ["sku"], unique=True)

    op.create_table(
        "inventory",
        _uuid_pk(),
        sa.Column("product_id", sa.Uuid(), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("warehouse_id", sa.Uuid(), sa.ForeignKey("warehouses.id"), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False, server_default="0"),
        sa.Column("reserved_quantity", sa.Float(), nullable=False, server_default="0"),
        sa.Column("batch_number", sa.String(100)),
        sa.Column("expiry_date", sa.DateTime(timezone=True)),
        sa.Column("last_count_date", sa.DateTime(timezone=True)),
        *_timestamps(),
        *_soft_delete(),
        sa.UniqueConstraint("product_id", "warehouse_id", "batch_number", name="uix_inventory_product_warehouse_batch"),
    )

    op.create_table(
        "purchase_orders",
        _uuid_pk(),
        sa.Column("order_number", sa.String(50), nullable=False),
        sa.Column("vendor_id", sa.Uuid(), sa.ForeignKey("vendors.id"), nullable=False),
        sa.Column("vendor_name", sa.String(200)),
        sa.Column("warehouse_id", sa.Uuid(), sa.ForeignKey("warehouses.id")),
        sa.Column("warehouse_name", sa.String(200)),
        sa.Column("status", sa.String(30), nullable=False, server_default="pending"),
        sa.Column("priority", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("subtotal", sa.Float(), nullable=False, server_default="0"),
        sa.Column("tax_amount", sa.Float(), nullable=False, server_default="0"),
        sa.Column("discount", sa.Float(), nullable=False, server_default="0"),
        sa.Column("total_amount", sa.Float(), nullable=False, server_default="0"),
        sa.Column("currency", sa.String(3), nullable=False, server_default="INR"),
        sa.Column("notes", sa.Text()),
        sa.Column("terms", sa.Text()),
        sa.Column("ordered_by", sa.Uuid(), sa.ForeignKey("users.id")),
        sa.Column("ordered_by_name", sa.String(100)),
        sa.Column("created_by", sa.Uuid(), sa.ForeignKey("users.id")),
        sa.Column("approved_by", sa.Uuid(), sa.ForeignKey("users.id")),
        sa.Column("approved_by_name", sa.String(100)),
        sa.Column("approved_at", sa.DateTime(timezone=True)),
        sa.Column("expected_delivery_date", sa.Date()),
        sa.Column("delivered_date", sa.DateTime(timezone=True)),
        sa.Column("is_urgent", sa.Boolean(), nullable=False, server_default=sa.false()),
        *_timestamps(),
        *_soft_delete(),
    )
    op.create_index("ix_purchase_orders_order_number", "purchase_orders", ["order_number"], unique=True)

    op.create_table(
        "purchase_order_items",
        _uuid_pk(),
        sa.Column("order_id", sa.Uuid(), sa.ForeignKey("purchase_orders.id"), nullable=False),
        sa.Column("product_id", sa.Uuid(), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("product_name", sa.String(200)),
        sa.Column("product_sku", sa.String(50)),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("unit_price", sa.Float(), nullable=False),
        sa.Column("total_price", sa.Float(), nullable=False),
        sa.Column("received_quantity", sa.Float(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(30), nullable=False, server_default="pending"),
        *_timestamps(),
        *_soft_delete(),
    )

    op.create_table(
        "shipments",
        _uuid_pk(),
        sa.Column("tracking_number", sa.String(100), nullable=False),
        sa.Column("order_id", sa.Uuid(), sa.ForeignKey("purchase_orders.id"), nullable=False),
        sa.Column("order_number", sa.String(50)),
        sa.Column("carrier", sa.String(100), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="pending"),
        sa.Column("origin_warehouse_id", sa.Uuid(), sa.ForeignKey("warehouses.id")),
        sa.Column("warehouse_name", sa.String(200)),
        sa.Column("destination_address", sa.Text()),
        sa.Column("estimated_delivery", sa.Date()),
        sa.Column("actual_delivery", sa.DateTime(timezone=True)),
        sa.Column("shipped_date", sa.DateTime(timezone=True)),
        sa.Column("shipped_by", sa.Uuid(), sa.ForeignKey("users.id")),
        sa.Column("shipped_by_name", sa.String(100)),
        sa.Column("weight", sa.Float()),
        sa.Column("dimensions", sa.String(100)),
        sa.Column("notes", sa.Text()),
        sa.Column("current_location", sa.Text()),
        sa.Column("last_updated", sa.DateTime(timezone=True)),
        *_timestamps(),
        *_soft_delete(),
    )
    op.create_index("ix_shipments_tracking_number", "shipments", ["tracking_number"], unique=True)

    op.create_table(
        "invoices",
        _uuid_pk(),
        sa.Column("invoice_number", sa.String(50), nullable=False),
        sa.Column("order_id", sa.Uuid(), sa.ForeignKey("purchase_orders.id"), nullable=False),
        sa.Column("order_number", sa.String(50)),
        sa.Column("vendor_id", sa.Uuid(), sa.ForeignKey("vendors.id"), nullable=False),
        sa.Column("vendor_name", sa.String(200)),
        sa.Column("status", sa.String(30), nullable=False, server_default="draft"),
        sa.Column("issue_date", sa.Date()),
        sa.Column("due_date", sa.Date()),
        sa.Column("paid_date", sa.DateTime(timezone=True)),
        sa.Column("subtotal", sa.Float(), nullable=False, server_default="0"),
        sa.Column("tax_amount", sa.Float(), nullable=False, server_default="0"),
        sa.Column("discount", sa.Float(), nullable=False, server_default="0"),
        sa.Column("total_amount", sa.Float(), nullable=False, server_default="0"),
        sa.Column("amount_paid", sa.Float(), nullable=False, server_default="0"),
        sa.Column("balance_due", sa.Float(), nullable=False, server_default="0"),
        sa.Column("currency", sa.String(3), nullable=False, server_default="INR"),
        sa.Column("notes", sa.Text()),
        sa.Column("pdf_url", sa.Text()),
        sa.Column("payment_method", sa.String(50)),
        sa.Column("payment_reference", sa.String(200)),
        sa.Column("created_by", sa.Uuid(), sa.ForeignKey("users.id")),
        *_timestamps(),
        *_soft_delete(),
    )
    op.create_index("ix_invoices_invoice_number", "invoices", ["invoice_number"], unique=True)

    op.create_table(
        "notifications",
        _uuid_pk(),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id")),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("type", sa.String(30), nullable=False, server_default="info"),
        sa.Column("category", sa.String(30), nullable=False, server_default="system"),
        sa.Column("reference_type", sa.String(100)),
        sa.Column("reference_id", sa.Uuid()),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("read_at", sa.DateTime(timezone=True)),
        sa.Column("action_url", sa.Text()),
        *_timestamps(),
        *_soft_delete(),
    )

    op.create_table(
        "audit_logs",
        _uuid_pk(),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id")),
        sa.Column("action", sa.String(255), nullable=False),
        sa.Column("entity_type", sa.String(100), nullable=False),
        sa.Column("entity_id", sa.Uuid()),
        sa.Column("changes", sa.JSON()),
        sa.Column("ip_address", sa.String(100)),
        sa.Column("user_agent", sa.Text()),
        sa.Column("description", sa.Text()),
        *_timestamps(),
        *_soft_delete(),
    )


def downgrade() -> None:
    for table in [
        "audit_logs",
        "notifications",
        "invoices",
        "shipments",
        "purchase_order_items",
        "purchase_orders",
        "inventory",
        "products",
        "warehouses",
        "vendors",
        "users",
        "roles",
    ]:
        op.drop_table(table)
