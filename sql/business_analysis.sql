
-- =====================================================
-- PROJECT: Real-Time Revenue Leakage & Customer Journey
-- PURPOSE: Initial business analysis
-- DATABASE: revenue_intelligence
-- =====================================================


-- 1. Order and payment summary
SELECT
    (SELECT COUNT(*) FROM orders) AS total_orders,
    (SELECT COUNT(*) FROM orders
     WHERE order_status = 'Completed') AS completed_orders,
    (SELECT COUNT(*) FROM orders
     WHERE order_status = 'Payment Failed') AS failed_orders,
    (SELECT COUNT(*) FROM payments
     WHERE payment_status = 'Success') AS successful_payments,
    (SELECT COUNT(*) FROM payments
     WHERE payment_status = 'Failed') AS failed_payments;


-- 2. Successful and failed payment amounts
SELECT
    payment_status,
    COUNT(*) AS payment_count,
    ROUND(SUM(transaction_amount), 2) AS total_amount
FROM payments
GROUP BY payment_status
ORDER BY payment_status;


-- 3. Shipment performance
SELECT
    COUNT(*) AS total_shipments,
    COUNT(*) FILTER (
        WHERE shipment_status = 'Delivered'
    ) AS delivered_shipments,
    COUNT(*) FILTER (
        WHERE shipment_status = 'Delayed'
    ) AS delayed_shipments,
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE shipment_status = 'Delayed'
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS delay_rate_percent,
    ROUND(AVG(delivery_delay_days), 2) AS average_delay_days
FROM shipments;


-- 4. Return and refund analysis
SELECT
    COUNT(*) AS total_returns,
    ROUND(SUM(refund_amount), 2) AS total_refunds,
    ROUND(AVG(refund_amount), 2) AS average_refund
FROM returns;


-- 5. Customer journey funnel
SELECT
    COUNT(DISTINCT session_id) FILTER (
        WHERE event_type = 'product_view'
    ) AS product_view_sessions,

    COUNT(DISTINCT session_id) FILTER (
        WHERE event_type = 'add_to_cart'
    ) AS cart_sessions,

    COUNT(DISTINCT session_id) FILTER (
        WHERE event_type = 'checkout_start'
    ) AS checkout_sessions,

    ROUND(
        100.0 * COUNT(DISTINCT session_id) FILTER (
            WHERE event_type = 'add_to_cart'
        ) / NULLIF(
            COUNT(DISTINCT session_id) FILTER (
                WHERE event_type = 'product_view'
            ), 0
        ), 2
    ) AS view_to_cart_percent,

    ROUND(
        100.0 * COUNT(DISTINCT session_id) FILTER (
            WHERE event_type = 'checkout_start'
        ) / NULLIF(
            COUNT(DISTINCT session_id) FILTER (
                WHERE event_type = 'product_view'
            ), 0
        ), 2
    ) AS view_to_checkout_percent

FROM events;


-- 6. Product performance
SELECT
    p.product_name,
    p.category,
    COUNT(o.order_id) AS completed_order_count,
    SUM(o.quantity) AS units_sold,
    ROUND(SUM(o.total_amount), 2) AS sales_amount
FROM orders o
JOIN products p
    ON o.product_id = p.product_id
WHERE o.order_status = 'Completed'
GROUP BY p.product_id, p.product_name, p.category
ORDER BY sales_amount DESC
LIMIT 10;


-- 7. Failed payments by payment method
SELECT
    payment_method,
    COUNT(*) AS failed_payment_count,
    ROUND(SUM(transaction_amount), 2) AS failed_amount
FROM payments
WHERE payment_status = 'Failed'
GROUP BY payment_method
ORDER BY failed_amount DESC;


-- 8. Data quality: correct categories using product names
UPDATE products
SET category = CASE
    WHEN product_name ILIKE '%earbuds%'
      OR product_name ILIKE '%smart watch%'
      OR product_name ILIKE '%fitness band%'
        THEN 'Electronics'

    WHEN product_name ILIKE '%running shoes%'
        THEN 'Footwear'

    WHEN product_name ILIKE '%backpack%'
      OR product_name ILIKE '%travel bag%'
        THEN 'Bags'

    ELSE category
END
WHERE product_name ILIKE '%earbuds%'
   OR product_name ILIKE '%smart watch%'
   OR product_name ILIKE '%fitness band%'
   OR product_name ILIKE '%running shoes%'
   OR product_name ILIKE '%backpack%'
   OR product_name ILIKE '%travel bag%';


-- 9. Verify the corrected categories
SELECT product_name, category
FROM products
WHERE product_name ILIKE '%earbuds%'
   OR product_name ILIKE '%smart watch%'
   OR product_name ILIKE '%fitness band%'
   OR product_name ILIKE '%running shoes%'
   OR product_name ILIKE '%backpack%'
   OR product_name ILIKE '%travel bag%'
ORDER BY product_name
LIMIT 20;




-- =====================================================
-- POWER BI DATA VIEWS
-- =====================================================


-- VIEW 1: Overall order performance
CREATE OR REPLACE VIEW vw_order_performance AS
SELECT
    COUNT(*) AS total_orders,
    COUNT(*) FILTER (
        WHERE order_status = 'Completed'
    ) AS completed_orders,
    COUNT(*) FILTER (
        WHERE order_status = 'Payment Failed'
    ) AS failed_orders,
    ROUND(
        AVG(total_amount) FILTER (
            WHERE order_status = 'Completed'
        ), 2
    ) AS average_completed_order_value,
    ROUND(
        SUM(total_amount) FILTER (
            WHERE order_status = 'Completed'
        ), 2
    ) AS completed_order_sales
FROM orders;


-- VIEW 2: Product performance
CREATE OR REPLACE VIEW vw_product_performance AS
SELECT
    p.product_id,
    p.product_name,
    p.category,
    COUNT(o.order_id) AS completed_order_count,
    COALESCE(SUM(o.quantity), 0) AS units_sold,
    ROUND(COALESCE(SUM(o.total_amount), 0), 2)
        AS completed_order_sales
FROM products p
LEFT JOIN orders o
    ON p.product_id = o.product_id
   AND o.order_status = 'Completed'
GROUP BY
    p.product_id,
    p.product_name,
    p.category;


-- VIEW 3: Payment performance by method
CREATE OR REPLACE VIEW vw_payment_method_performance AS
SELECT
    payment_method,
    COUNT(*) AS total_payment_attempts,
    COUNT(*) FILTER (
        WHERE payment_status = 'Success'
    ) AS successful_payments,
    COUNT(*) FILTER (
        WHERE payment_status = 'Failed'
    ) AS failed_payments,
    ROUND(
        SUM(transaction_amount) FILTER (
            WHERE payment_status = 'Success'
        ), 2
    ) AS successful_payment_amount,
    ROUND(
        SUM(transaction_amount) FILTER (
            WHERE payment_status = 'Failed'
        ), 2
    ) AS failed_payment_amount
FROM payments
GROUP BY payment_method;


-- VIEW 4: Delivery performance
CREATE OR REPLACE VIEW vw_delivery_performance AS
SELECT
    COUNT(*) AS total_shipments,
    COUNT(*) FILTER (
        WHERE shipment_status = 'Delivered'
    ) AS delivered_shipments,
    COUNT(*) FILTER (
        WHERE shipment_status = 'Delayed'
    ) AS delayed_shipments,
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE shipment_status = 'Delayed'
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS delay_rate_percent,
    ROUND(AVG(delivery_delay_days), 2)
        AS average_delay_days
FROM shipments;


-- VIEW 5: Returns and refunds
CREATE OR REPLACE VIEW vw_returns_performance AS
SELECT
    COUNT(*) AS total_returns,
    ROUND(SUM(refund_amount), 2) AS total_refunds,
    ROUND(AVG(refund_amount), 2) AS average_refund
FROM returns;


-- VIEW 6: Customer journey funnel
CREATE OR REPLACE VIEW vw_customer_journey AS
SELECT
    COUNT(DISTINCT session_id) FILTER (
        WHERE event_type = 'product_view'
    ) AS product_view_sessions,
    COUNT(DISTINCT session_id) FILTER (
        WHERE event_type = 'add_to_cart'
    ) AS cart_sessions,
    COUNT(DISTINCT session_id) FILTER (
        WHERE event_type = 'checkout_start'
    ) AS checkout_sessions,
    ROUND(
        100.0 * COUNT(DISTINCT session_id) FILTER (
            WHERE event_type = 'add_to_cart'
        ) / NULLIF(
            COUNT(DISTINCT session_id) FILTER (
                WHERE event_type = 'product_view'
            ), 0
        ),
        2
    ) AS view_to_cart_percent,
    ROUND(
        100.0 * COUNT(DISTINCT session_id) FILTER (
            WHERE event_type = 'checkout_start'
        ) / NULLIF(
            COUNT(DISTINCT session_id) FILTER (
                WHERE event_type = 'product_view'
            ), 0
        ),
        2
    ) AS view_to_checkout_percent
FROM events;



CREATE OR REPLACE VIEW vw_revenue_reconciliation AS
WITH order_metrics AS (
    SELECT
        ROUND(
            SUM(total_amount) FILTER (
                WHERE order_status = 'Completed'
            ), 2
        ) AS completed_order_sales
    FROM orders
),
payment_metrics AS (
    SELECT
        COUNT(*) FILTER (
            WHERE payment_status = 'Success'
        ) AS successful_payment_count,
        ROUND(
            SUM(transaction_amount) FILTER (
                WHERE payment_status = 'Success'
            ), 2
        ) AS successful_payment_amount,
        COUNT(*) FILTER (
            WHERE payment_status = 'Failed'
        ) AS failed_payment_attempts,
        ROUND(
            SUM(transaction_amount) FILTER (
                WHERE payment_status = 'Failed'
            ), 2
        ) AS failed_payment_attempt_amount,
        COUNT(*) FILTER (
            WHERE payment_status = 'Failed'
              AND order_id IS NULL
        ) AS unmatched_failed_payments,
        ROUND(
            SUM(transaction_amount) FILTER (
                WHERE payment_status = 'Failed'
                  AND order_id IS NULL
            ), 2
        ) AS unmatched_failed_payment_amount
    FROM payments
),
refund_metrics AS (
    SELECT
        ROUND(COALESCE(SUM(refund_amount), 0), 2)
            AS total_refunds
    FROM returns
)
SELECT
    o.completed_order_sales,
    p.successful_payment_count,
    p.successful_payment_amount,
    r.total_refunds,
    ROUND(
        o.completed_order_sales - r.total_refunds, 2
    ) AS estimated_net_sales_after_refunds,
    p.failed_payment_attempts,
    p.failed_payment_attempt_amount,
    p.unmatched_failed_payments,
    p.unmatched_failed_payment_amount
FROM order_metrics o
CROSS JOIN payment_metrics p
CROSS JOIN refund_metrics r;