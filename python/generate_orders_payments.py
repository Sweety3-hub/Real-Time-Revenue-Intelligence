
import os
import random

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
            cursor.execute("""
                SELECT
                    e.session_id,
                    e.customer_id,
                    e.product_id
                FROM events e
                JOIN sessions s
                    ON e.session_id = s.session_id
                WHERE e.event_type = 'checkout_start'
                  AND s.traffic_source = 'Portfolio Generated'
                  AND NOT EXISTS (
                      SELECT 1
                      FROM orders o
                      WHERE o.session_id = e.session_id
                  )
                ORDER BY e.session_id;
            """)
            checkouts = cursor.fetchall()

            cursor.execute("""
                SELECT product_id, price
                FROM products;
            """)
            prices = {
                row[0]: row[1]
                for row in cursor.fetchall()
            }

            created_orders = 0
            created_payments = 0

            methods = ["UPI", "Credit Card", "Debit Card", "Net Banking"]

            for session_id, customer_id, product_id in checkouts:
                quantity = random.randint(1, 2)
                unit_price = prices[product_id]
                total = unit_price * quantity

                success = random.random() < 0.85

                cursor.execute("""
                    SELECT session_start
                    FROM sessions
                    WHERE session_id = %s;
                """, (session_id,))
                order_date = cursor.fetchone()[0]

                cursor.execute("""
                    INSERT INTO orders (
                        customer_id, product_id, session_id,
                        order_date, quantity, unit_price,
                        total_amount, order_status
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING order_id;
                """, (
                    customer_id, product_id, session_id,
                    order_date, quantity, unit_price,
                    total, "Completed" if success else "Payment Failed"
                ))

                order_id = cursor.fetchone()[0]
                created_orders += 1

                cursor.execute("""
                    INSERT INTO payments (
                        order_id, customer_id, payment_time,
                        payment_method, payment_status,
                        transaction_amount, failure_reason
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s);
                """, (
                    order_id,
                    customer_id,
                    order_date,
                    random.choice(methods),
                    "Success" if success else "Failed",
                    total,
                    None if success else "Payment gateway timeout"
                ))

                created_payments += 1

            print(f"New orders created: {created_orders}")
            print(f"New payments created: {created_payments}")

finally:
    connection.close()
