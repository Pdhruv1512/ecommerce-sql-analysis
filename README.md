# E-Commerce Business Analysis (SQL)

A SQL-driven analysis of an e-commerce dataset (customers, orders, products) answering
common business questions: who our best customers are, which categories drive revenue,
whether revenue is growing, and where returns are concentrated.

## Why this project
Entry-level analytics roles spend a lot of time turning raw transactional data into
answers stakeholders can act on. This project simulates that workflow end-to-end:
schema design → data generation → SQL analysis → business takeaways.

## Dataset
Synthetic but realistic e-commerce data generated with `generate_data.py` (seeded for
reproducibility), loaded into a SQLite database (`ecommerce.db`). CSV exports of each
table are also included for quick viewing on GitHub.

| Table | Rows | Description |
|---|---|---|
| `customers` | 800 | customer_id, name, region, signup_date |
| `products` | 64 | product_id, name, category, unit_price |
| `orders` | 1,682 | order_id, customer_id, order_date, payment_method, is_returned |
| `order_items` | 4,183 | order_item_id, order_id, product_id, quantity |

## Tools
SQL (SQLite), Python (for data generation and running queries)

## Business Questions & Key Findings

**1. Top customers by revenue** — The top 10 customers each generated $5.6K–$7.9K in
lifetime revenue, with order counts ranging from 4 to 10 — a small group of high-frequency
buyers contributes disproportionately to revenue.

**2. Month-over-month revenue growth** — Revenue grew from ~$5.3K (Feb 2023) to ~$34K
(Jan 2024), with the steepest single-month jump in June 2023 (+355%) as the customer
base scaled. Growth was generally positive month over month after mid-2023.

**3. Revenue by category** — Home & Kitchen ($162.8K) and Sports & Outdoors ($161.6K)
were the top-grossing categories, while Toys ($120K) lagged. Revenue was fairly evenly
spread across all 8 categories (no single category dominates).

**4. Repeat purchase rate** — 66.4% of customers who placed an order placed more than
one, indicating strong repeat engagement — a healthy sign for retention-focused strategy.

**5. Returns by payment method** — Debit card orders had the highest return rate (7.2%),
compared to PayPal (3.2%), suggesting payment method may be worth investigating further
as a return-risk factor.

**6. Revenue by region** — The West region had the highest revenue per customer ($1,831),
while the Midwest had both the fewest customers and the lowest revenue per customer
($1,551) — a potential target for regional marketing investment.

**7. Signup cohort analysis** — Customers who signed up in August 2023 generated the
highest average revenue per customer ($1,879) among all monthly cohorts, useful for
understanding which acquisition periods produced the most valuable customers.

## Files
```
├── generate_data.py     # builds the synthetic dataset into ecommerce.db
├── ecommerce.db          # SQLite database (generated)
├── queries.sql           # all 7 business-question queries, commented
├── customers.csv         # table export
├── products.csv          # table export
├── orders.csv            # table export
├── order_items.csv       # table export
└── README.md
```

## How to run it yourself
```bash
python3 generate_data.py        # builds ecommerce.db
sqlite3 ecommerce.db < queries.sql   # runs all queries
```
Or open `ecommerce.db` in [DB Browser for SQLite](https://sqlitebrowser.org/) and run
`queries.sql` interactively.

## Possible extensions
- Connect to a BI tool (Tableau/Power BI) for a visual dashboard on top of these queries
- Add a customer lifetime value (CLV) calculation
- Migrate the schema to PostgreSQL/MySQL to practice a client-server database
