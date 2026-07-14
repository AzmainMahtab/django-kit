"""Management command to migrate the Elite4Print slice from the legacy DB."""

import os
from contextlib import closing
from decimal import Decimal

import psycopg
from django.core.management.base import BaseCommand

from backend.apps.catalog.domain.models import Product, ProductCategory
from backend.apps.ordering.domain.models import Job, JobMemo, Order
from backend.apps.payment.domain.models import Payment, PendingRefund
from backend.apps.promotion.domain.models import Coupon, CouponUsage


LEGACY_DSN = os.getenv(
    "LEGACY_DATABASE_URL",
    "postgresql://e4p:e4p@localhost:5433/e4p_legacy",
)


class Command(BaseCommand):
    help = "Migrate the Elite4Print order+payment+product+coupon slice."

    def add_arguments(self, parser):
        parser.add_argument(
            "--legacy-dsn",
            type=str,
            default=LEGACY_DSN,
            help="Connection string for the legacy source database.",
        )

    def handle(self, *args, **options):
        legacy_dsn = options["legacy_dsn"]
        self.stdout.write(f"Connecting to legacy DB: {legacy_dsn}")

        with closing(psycopg.connect(legacy_dsn)) as conn:
            self.migrate_users(conn)
            self.migrate_catalog(conn)
            self.migrate_orders(conn)
            self.migrate_jobs(conn)
            self.migrate_job_memos(conn)
            self.migrate_payments(conn)
            self.migrate_pending_refunds(conn)
            self.migrate_coupons(conn)
            self.migrate_coupon_products(conn)
            self.migrate_coupon_usages(conn)

        self.print_summary()

    def _fetchall(self, conn, sql):
        with conn.cursor() as cur:
            cur.execute(sql)
            cols = [desc[0] for desc in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]

    def migrate_users(self, conn):
        # Users live in the identity app; we just need them present for FK sanity.
        # In this POC we create stub users by id/email if they don't exist.
        from backend.apps.identity.domain.models import User

        rows = self._fetchall(conn, "SELECT id, email FROM authentications_user ORDER BY id")
        for row in rows:
            User.objects.update_or_create(
                id=row["id"],
                defaults={
                    "email": row["email"],
                    "username": row["email"],
                    "is_active": True,
                },
            )
        self.stdout.write(f"  users: {len(rows)}")

    def migrate_catalog(self, conn):
        category_rows = self._fetchall(
            conn, "SELECT id, name, created_at, updated_at FROM product_management_productcategory ORDER BY id"
        )
        for row in category_rows:
            ProductCategory.objects.update_or_create(
                id=row["id"],
                defaults={"name": row["name"]},
            )

        product_rows = self._fetchall(conn, """
            SELECT id, category_id, name, description, product_id, created_by_id,
                   product_type, min_price, max_price, sqr_ft_price, shop_rate_per_hr,
                   is_active, on_draft, base_turnaround, combined_shipping, ordering,
                   show_faq, shipping_type, created_at, updated_at
            FROM product_management_product ORDER BY id
        """)
        for row in product_rows:
            Product.objects.update_or_create(
                id=row["id"],
                defaults={
                    "category_id": row["category_id"],
                    "name": row["name"],
                    "description": row["description"] or "",
                    "product_code": row["product_id"],
                    "created_by_id": row["created_by_id"],
                    "product_type": row["product_type"],
                    "min_price": row["min_price"] or Decimal("0"),
                    "max_price": row["max_price"] or Decimal("0"),
                    "sqr_ft_price": row["sqr_ft_price"] or Decimal("0"),
                    "shop_rate_per_hr": row["shop_rate_per_hr"] or Decimal("0"),
                    "is_active": row["is_active"],
                    "on_draft": row["on_draft"],
                    "base_turnaround": row["base_turnaround"],
                    "combined_shipping": row["combined_shipping"],
                    "ordering": row["ordering"],
                    "show_faq": row["show_faq"],
                    "shipping_type": row["shipping_type"],
                },
            )
        self.stdout.write(f"  categories: {len(category_rows)}, products: {len(product_rows)}")

    def migrate_orders(self, conn):
        rows = self._fetchall(conn, """
            SELECT id, user_id, total_price, total_shipping_price, final_price,
                   discount_amount, payment_status, extra_payment, tax_amount,
                   is_additional_payment_paid, original_total_price, original_shipping_price,
                   original_tax_amount, points_used, total_adjustment_amount,
                   total_refunded_amount, order_id, order_ref, created_at, updated_at
            FROM order_management_order ORDER BY id
        """)
        for row in rows:
            Order.objects.update_or_create(
                id=row["id"],
                defaults={
                    "order_number": row["order_id"],
                    "user_id": row["user_id"],
                    "status": "PENDING",
                    "total_price": row["total_price"] or Decimal("0"),
                    "total_shipping_price": row["total_shipping_price"] or Decimal("0"),
                    "final_price": row["final_price"] or Decimal("0"),
                    "discount_amount": row["discount_amount"] or Decimal("0"),
                    "payment_status": row["payment_status"],
                    "extra_payment": row["extra_payment"] or Decimal("0"),
                    "tax_amount": row["tax_amount"] or Decimal("0"),
                    "is_additional_payment_paid": row["is_additional_payment_paid"],
                    "original_total_price": row["original_total_price"] or Decimal("0"),
                    "original_shipping_price": row["original_shipping_price"] or Decimal("0"),
                    "original_tax_amount": row["original_tax_amount"] or Decimal("0"),
                    "points_used": row["points_used"] or 0,
                    "total_adjustment_amount": row["total_adjustment_amount"] or Decimal("0"),
                    "total_refunded_amount": row["total_refunded_amount"] or Decimal("0"),
                    "order_ref": row["order_ref"] or {},
                },
            )
        self.stdout.write(f"  orders: {len(rows)}")

    def migrate_jobs(self, conn):
        rows = self._fetchall(conn, """
            SELECT id, order_id, job_id, job_name, job_status, group_id, process_status,
                   product_id, item_code, paper, size, quantity, coating, color, trim_size,
                   price, original_price, notes, admin_notes, turnaround, turnaround_day,
                   due_date, cut_off_time, file_editable, shipping_editable, pickup_location,
                   created_at, updated_at
            FROM order_management_orderitems ORDER BY id
        """)
        for row in rows:
            Job.objects.update_or_create(
                id=row["id"],
                defaults={
                    "order_id": row["order_id"],
                    "job_id": row["job_id"],
                    "job_name": row["job_name"] or "",
                    "job_status": row["job_status"],
                    "group_id": row["group_id"] or "",
                    "process_status": row["process_status"],
                    "product_id": row["product_id"],
                    "item_code": row["item_code"],
                    "paper": row["paper"],
                    "size": row["size"] or "",
                    "quantity": row["quantity"] or 0,
                    "coating": row["coating"],
                    "color": row["color"],
                    "trim_size": row["trim_size"] or "",
                    "price": row["price"] or Decimal("0"),
                    "original_price": row["original_price"] or Decimal("0"),
                    "notes": row["notes"],
                    "admin_notes": row["admin_notes"],
                    "turnaround": row["turnaround"],
                    "turnaround_day": row["turnaround_day"] or 0,
                    "due_date": row["due_date"],
                    "cut_off_time": row["cut_off_time"],
                    "file_editable": row["file_editable"],
                    "shipping_editable": row["shipping_editable"],
                    "pickup_location": row["pickup_location"],
                },
            )
        self.stdout.write(f"  jobs: {len(rows)}")

    def migrate_job_memos(self, conn):
        rows = self._fetchall(conn, """
            SELECT id, order_item_id, note, status, printing_adjustment, shipping_adjustment,
                   adjustment_type, total_adjustment, created_at, updated_at
            FROM order_management_orderitemmemo ORDER BY id
        """)
        for row in rows:
            JobMemo.objects.update_or_create(
                id=row["id"],
                defaults={
                    "job_id": row["order_item_id"],
                    "note": row["note"],
                    "status": row["status"],
                    "printing_adjustment": row["printing_adjustment"] or Decimal("0"),
                    "shipping_adjustment": row["shipping_adjustment"] or Decimal("0"),
                    "adjustment_type": row["adjustment_type"],
                    "total_adjustment": row["total_adjustment"] or Decimal("0"),
                },
            )
        self.stdout.write(f"  job memos: {len(rows)}")

    def migrate_payments(self, conn):
        rows = self._fetchall(conn, """
            SELECT id, amount, status, method, type, trans_id, order_id, card_number,
                   job_change_id, transactions_history, user_id, created_at, updated_at
            FROM payment_management_payment ORDER BY id
        """)
        for row in rows:
            Payment.objects.update_or_create(
                id=row["id"],
                defaults={
                    "amount": Decimal(str(row["amount"])) if row["amount"] else Decimal("0"),
                    "status": row["status"],
                    "method": row["method"],
                    "type": row["type"],
                    "trans_id": row["trans_id"],
                    "order_id": row["order_id"],
                    "card_number": row["card_number"],
                    "job_change_id": row["job_change_id"],
                    "transactions_history": row["transactions_history"] or {},
                    "user_id": row["user_id"],
                },
            )
        self.stdout.write(f"  payments: {len(rows)}")

    def migrate_pending_refunds(self, conn):
        rows = self._fetchall(conn, """
            SELECT id, order_id, payment_id, amount, card_number, status, transaction_id,
                   error_message, retry_count, points, created_at, updated_at
            FROM payment_management_pendingrefund ORDER BY id
        """)
        for row in rows:
            PendingRefund.objects.update_or_create(
                id=row["id"],
                defaults={
                    "order_id": row["order_id"],
                    "payment_id": row["payment_id"],
                    "amount": row["amount"] or Decimal("0"),
                    "card_number": row["card_number"],
                    "status": row["status"],
                    "transaction_id": row["transaction_id"],
                    "error_message": row["error_message"],
                    "retry_count": row["retry_count"] or 0,
                    "points": row["points"],
                },
            )
        self.stdout.write(f"  pending refunds: {len(rows)}")

    def migrate_coupons(self, conn):
        rows = self._fetchall(conn, """
            SELECT id, coupon_code, coupon_on, coupon_type, coupon_value, max_discount,
                   coupon_start_date, coupon_expiry_date, limit_per_user, limit_per_coupon,
                   coupon_description, created_at, updated_at
            FROM coupon_management_coupon ORDER BY id
        """)
        for row in rows:
            Coupon.objects.update_or_create(
                id=row["id"],
                defaults={
                    "coupon_code": row["coupon_code"],
                    "coupon_on": row["coupon_on"],
                    "coupon_type": row["coupon_type"],
                    "coupon_value": Decimal(str(row["coupon_value"])) if row["coupon_value"] else Decimal("0"),
                    "max_discount": Decimal(str(row["max_discount"])) if row["max_discount"] else Decimal("0"),
                    "coupon_start_date": row["coupon_start_date"],
                    "coupon_expiry_date": row["coupon_expiry_date"],
                    "limit_per_user": row["limit_per_user"],
                    "limit_per_coupon": row["limit_per_coupon"],
                    "coupon_description": row["coupon_description"],
                },
            )
        self.stdout.write(f"  coupons: {len(rows)}")

    def migrate_coupon_products(self, conn):
        rows = self._fetchall(
            conn, "SELECT coupon_id, product_id FROM coupon_management_coupon_products ORDER BY id"
        )
        for row in rows:
            coupon = Coupon.objects.get(id=row["coupon_id"])
            product = Product.objects.get(id=row["product_id"])
            coupon.usages.filter(id=product.id).exists()  # no-op placeholder
        # Note: Many-to-many products not modeled in POC; coupon products skipped.
        self.stdout.write(f"  coupon products: {len(rows)} (skipped - not modeled)")

    def migrate_coupon_usages(self, conn):
        rows = self._fetchall(conn, """
            SELECT id, coupon_id, user_id, order_id, status, created_at, updated_at
            FROM coupon_management_couponusage ORDER BY id
        """)
        for row in rows:
            CouponUsage.objects.update_or_create(
                id=row["id"],
                defaults={
                    "coupon_id": row["coupon_id"],
                    "user_id": row["user_id"],
                    "order_id": row["order_id"],
                    "status": row["status"],
                },
            )
        self.stdout.write(f"  coupon usages: {len(rows)}")

    def print_summary(self):
        self.stdout.write(self.style.SUCCESS("\nMigration complete. Target counts:"))
        self.stdout.write(f"  ProductCategory: {ProductCategory.objects.count()}")
        self.stdout.write(f"  Product: {Product.objects.count()}")
        self.stdout.write(f"  Order: {Order.objects.count()}")
        self.stdout.write(f"  Job: {Job.objects.count()}")
        self.stdout.write(f"  JobMemo: {JobMemo.objects.count()}")
        self.stdout.write(f"  Payment: {Payment.objects.count()}")
        self.stdout.write(f"  PendingRefund: {PendingRefund.objects.count()}")
        self.stdout.write(f"  Coupon: {Coupon.objects.count()}")
        self.stdout.write(f"  CouponUsage: {CouponUsage.objects.count()}")
