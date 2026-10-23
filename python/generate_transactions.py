
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
            cursor.execute("""
                SELECT s.session_id, s.customer_id,
                       s.session_start, s.session_end
                FROM sessions s
                WHERE s.traffic_source = 'Portfolio Generated'
                ORDER BY s.session_id;
            """)
            sessions = cursor.fetchall()

            cursor.execute("""
                SELECT DISTINCT session_id
                FROM events
                WHERE session_id IN (
                    SELECT session_id
                    FROM sessions
                    WHERE traffic_source = 'Portfolio Generated'
                );
            """)
            completed_sessions = {
                row[0] for row in cursor.fetchall()
            }

            cursor.execute("""
                SELECT product_id, price
                FROM products
                ORDER BY product_id;
            """)
            products = cursor.fetchall()

            if not products:
                raise ValueError("No products found in database.")

            created = 0

            for session_id, customer_id, start, end in sessions:
                if session_id in completed_sessions:
                    continue

                product = random.choice(products)
                product_id, price = product

                view_time = start + (end - start) * 0.15

                cursor.execute("""
                    INSERT INTO events (
                        session_id, customer_id, product_id,
                        event_type, event_time, quantity, event_value
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s);
                """, (
                    session_id, customer_id, product_id,
                    "product_view", view_time, 1, price
                ))
                created += 1

                # Some visitors add the product to their cart.
                if random.random() < 0.45:
                    cart_time = start + (end - start) * 0.40

                    cursor.execute("""
                        INSERT INTO events (
                            session_id, customer_id, product_id,
                            event_type, event_time, quantity, event_value
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s);
                    """, (
                        session_id, customer_id, product_id,
                        "add_to_cart", cart_time, 1, price
                    ))
                    created += 1

                    # Some cart users proceed to checkout.
                    if random.random() < 0.55:
                        checkout_time = start + (end - start) * 0.70

                        cursor.execute("""
                            INSERT INTO events (
                                session_id, customer_id, product_id,
                                event_type, event_time, quantity, event_value
                            )
                            VALUES (%s, %s, %s, %s, %s, %s, %s);
                        """, (
                            session_id, customer_id, product_id,
                            "checkout_start", checkout_time, 1, price
                        ))
                        created += 1

            cursor.execute("SELECT COUNT(*) FROM events;")
            total = cursor.fetchone()[0]

            print(f"New events created: {created}")
            print(f"Total events now: {total}")

finally:
    connection.close()
