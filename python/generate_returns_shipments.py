
import os
import random
from datetime import timedelta

import psycopg2

connection = psycopg2.connect(
    host="localhost",
    database="revenue_intelligence",
    user="postgres",
    password=os.environ["PGPASSWORD"]
)

try:
    with connection:
        with connection.cursor() as cursor:
            # Get completed generated orders.
            cursor.execute("""
                SELECT order_id, customer_id, product_id,
                       order_date, total_amount
                FROM orders
                WHERE order_id > 1
                  AND order_status = 'Completed'
                ORDER BY order_id;
            """)
            orders = cursor.fetchall()

            # Find orders that already have shipments.
            cursor.execute("SELECT order_id FROM shipments;")
            shipped_ids = {row[0] for row in cursor.fetchall()}

            partners = [
                "FastTrack Logistics",
                "BlueDart",
                "Delhivery",
                "India Post"
            ]

            new_shipments = 0

            for order_id, customer_id, product_id, order_date, total in orders:
                if order_id in shipped_ids:
                    continue

                shipment_date = order_date + timedelta(days=1)
                expected_date = order_date.date() + timedelta(days=4)
                actual_date = order_date.date() + timedelta(
                    days=random.randint(3, 7)
                )

                delay = max(0, (actual_date - expected_date).days)
                status = "Delayed" if delay > 0 else "Delivered"

                cursor.execute("""
                    INSERT INTO shipments (
                        order_id, customer_id, shipment_date,
                        expected_delivery_date, actual_delivery_date,
                        shipping_partner, shipment_status,
                        delivery_delay_days
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                """, (
                    order_id, customer_id, shipment_date,
                    expected_date, actual_date,
                    random.choice(partners), status, delay
                ))

                new_shipments += 1

            # Select a repeatable subset of completed orders for returns.
            cursor.execute("""
                SELECT order_id, customer_id, product_id,
                       order_date, total_amount
                FROM orders
                WHERE order_id > 1
                  AND order_status = 'Completed'
                  AND order_id % 10 = 0
                ORDER BY order_id;
            """)
            return_candidates = cursor.fetchall()

            cursor.execute("SELECT order_id FROM returns;")
            returned_ids = {row[0] for row in cursor.fetchall()}

            cursor.execute("""
                SELECT order_id, actual_delivery_date
                FROM shipments
                WHERE actual_delivery_date IS NOT NULL;
            """)
            delivery_dates = {
                row[0]: row[1] for row in cursor.fetchall()
            }

            reasons = [
                "Damaged product",
                "Wrong item",
                "Product not as expected",
                "Quality issue"
            ]

            new_returns = 0

            for order_id, customer_id, product_id, order_date, total in return_candidates:
                if order_id in returned_ids:
                    continue

                delivery_date = delivery_dates.get(order_id)
                if delivery_date is None:
                    continue

                return_date = delivery_date + timedelta(
                    days=random.randint(1, 10)
                )

                cursor.execute("""
                    INSERT INTO returns (
                        order_id, customer_id, product_id,
                        return_date, return_reason,
                        refund_amount, return_status
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s);
                """, (
                    order_id, customer_id, product_id,
                    return_date, random.choice(reasons),
                    total, "Refunded"
                ))

                new_returns += 1

            cursor.execute("SELECT COUNT(*) FROM shipments;")
            total_shipments = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM returns;")
            total_returns = cursor.fetchone()[0]

            print(f"New shipments created: {new_shipments}")
            print(f"Total shipments: {total_shipments}")
            print(f"New returns created: {new_returns}")
            print(f"Total returns: {total_returns}")

finally:
    connection.close()
