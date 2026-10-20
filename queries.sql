-- =========================================================
-- E-Commerce Business Analysis — SQL Queries
-- Database: ecommerce.db (SQLite)
-- Tables: customers, products, orders, order_items
-- =========================================================

-- 1. TOP 10 CUSTOMERS BY TOTAL REVENUE
-- Business question: Who are our highest-value customers?
SELECT
    c.customer_id,
    c.first_name || ' ' || c.last_name AS customer_name,
    c.region,
    ROUND(SUM(oi.quantity * p.unit_price), 2) AS total_revenue,
    COUNT(DISTINCT o.order_id) AS num_orders
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
JOIN products p ON p.product_id = oi.product_id
GROUP BY c.customer_id, c.first_name, c.last_name, c.region
ORDER BY total_revenue DESC
LIMIT 10;


-- 2. MONTH-OVER-MONTH REVENUE GROWTH
-- Business question: Is revenue growing, and by how much month to month?
WITH monthly_revenue AS (
    SELECT
        strftime('%Y-%m', o.order_date) AS month,
        ROUND(SUM(oi.quantity * p.unit_price), 2) AS revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    JOIN products p ON p.product_id = oi.product_id
    GROUP BY month
)
SELECT
    month,
    revenue,
    ROUND(
        100.0 * (revenue - LAG(revenue) OVER (ORDER BY month))
        / LAG(revenue) OVER (ORDER BY month), 1
    ) AS pct_change_vs_prev_month
FROM monthly_revenue
ORDER BY month;


-- 3. REVENUE AND ORDER COUNT BY PRODUCT CATEGORY
-- Business question: Which categories drive the most revenue vs. volume?
SELECT
    p.category,
    COUNT(DISTINCT oi.order_id) AS num_orders,
    SUM(oi.quantity) AS units_sold,
    ROUND(SUM(oi.quantity * p.unit_price), 2) AS total_revenue,
    ROUND(SUM(oi.quantity * p.unit_price) * 1.0 / SUM(oi.quantity), 2) AS avg_price_per_unit
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
GROUP BY p.category
ORDER BY total_revenue DESC;


-- 4. REPEAT PURCHASE RATE
-- Business question: What share of customers order more than once?
WITH order_counts AS (
    SELECT customer_id, COUNT(*) AS n_orders
    FROM orders
    GROUP BY customer_id
)
SELECT
    COUNT(*) AS total_customers_with_orders,
    SUM(CASE WHEN n_orders > 1 THEN 1 ELSE 0 END) AS repeat_customers,
    ROUND(100.0 * SUM(CASE WHEN n_orders > 1 THEN 1 ELSE 0 END) / COUNT(*), 1) AS repeat_purchase_rate_pct
FROM order_counts;


-- 5. RETURN RATE BY PAYMENT METHOD
-- Business question: Does payment method correlate with return likelihood?
SELECT
    payment_method,
    COUNT(*) AS total_orders,
    SUM(is_returned) AS returned_orders,
    ROUND(100.0 * SUM(is_returned) / COUNT(*), 1) AS return_rate_pct
FROM orders
GROUP BY payment_method
ORDER BY return_rate_pct DESC;


-- 6. REVENUE BY REGION
-- Business question: Which regions should marketing prioritize?
SELECT
    c.region,
    COUNT(DISTINCT c.customer_id) AS num_customers,
    ROUND(SUM(oi.quantity * p.unit_price), 2) AS total_revenue,
    ROUND(SUM(oi.quantity * p.unit_price) / COUNT(DISTINCT c.customer_id), 2) AS revenue_per_customer
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
JOIN products p ON p.product_id = oi.product_id
GROUP BY c.region
ORDER BY total_revenue DESC;


-- 7. CUSTOMER SIGNUP COHORT — REVENUE PER COHORT MONTH
-- Business question: Do earlier-signed-up customers generate more lifetime revenue?
-- Note: includes customers with no orders (LEFT JOIN), and later cohorts have had
-- less time to buy, so recent months are expected to look lower.
SELECT
    strftime('%Y-%m', c.signup_date) AS signup_month,
    COUNT(DISTINCT c.customer_id) AS customers_in_cohort,
    ROUND(SUM(oi.quantity * p.unit_price), 2) AS cohort_total_revenue,
    ROUND(SUM(oi.quantity * p.unit_price) / COUNT(DISTINCT c.customer_id), 2) AS avg_revenue_per_customer
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.customer_id
LEFT JOIN order_items oi ON oi.order_id = o.order_id
LEFT JOIN products p ON p.product_id = oi.product_id
GROUP BY signup_month
ORDER BY signup_month;


-- 8. AVERAGE ORDER VALUE AND CUSTOMER LIFETIME VALUE
-- Business question: How much is a typical order, and a typical customer, worth?
-- CLV here = average order value x average orders per customer (historical, no discounting).
WITH order_totals AS (
    SELECT
        o.order_id,
        o.customer_id,
        SUM(oi.quantity * p.unit_price) AS order_value
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    JOIN products p ON p.product_id = oi.product_id
    GROUP BY o.order_id, o.customer_id
)
SELECT
    COUNT(*) AS total_orders,
    COUNT(DISTINCT customer_id) AS customers_with_orders,
    ROUND(AVG(order_value), 2) AS avg_order_value,
    ROUND(1.0 * COUNT(*) / COUNT(DISTINCT customer_id), 2) AS avg_orders_per_customer,
    ROUND(SUM(order_value) / COUNT(DISTINCT customer_id), 2) AS avg_customer_lifetime_value
FROM order_totals;
