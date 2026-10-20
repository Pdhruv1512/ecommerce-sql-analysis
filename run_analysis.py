"""
Runs every query in queries.sql against ecommerce.db, saves each result to
results/ as a CSV, and draws charts for the key findings into images/.

Usage:
    python3 generate_data.py   # only needed if ecommerce.db is missing
    python3 run_analysis.py
"""
import csv
import os
import re
import sqlite3

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

DB_PATH = "ecommerce.db"
SQL_PATH = "queries.sql"
RESULTS_DIR = "results"
IMAGES_DIR = "images"
BLUE = "#4E79A7"


def load_queries(path):
    """Split queries.sql into (number, title, sql) using the '-- N. TITLE' headers."""
    text = open(path, encoding="utf-8").read()
    pattern = re.compile(r"^-- (\d+)\. (.+)$", re.MULTILINE)
    matches = list(pattern.finditer(text))
    queries = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sql = text[m.start():end].strip()
        queries.append((int(m.group(1)), m.group(2).strip(), sql))
    return queries


def slug(title):
    return re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")[:50]


def save_csv(path, headers, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)


def money(x, _pos=None):
    return f"${x/1000:,.0f}K" if x >= 1000 else f"${x:,.0f}"


def bar_chart(labels, values, title, xlabel, path, fmt=money):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.barh(labels[::-1], values[::-1], color=BLUE)
    ax.set_title(title, loc="left", fontsize=13)
    ax.set_xlabel(xlabel)
    ax.xaxis.set_major_formatter(FuncFormatter(fmt))
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for i, v in enumerate(values[::-1]):
        ax.text(v, i, " " + fmt(v), va="center", fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(IMAGES_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    results = {}

    for num, title, sql in load_queries(SQL_PATH):
        cur = conn.execute(sql)
        headers = [d[0] for d in cur.description]
        rows = cur.fetchall()
        results[num] = (headers, rows)
        out = os.path.join(RESULTS_DIR, f"q{num}_{slug(title)}.csv")
        save_csv(out, headers, rows)
        print(f"Q{num} {title}: {len(rows)} rows -> {out}")

    # Chart 1: monthly revenue (query 2)
    _, rows = results[2]
    months = [r[0] for r in rows]
    revenue = [r[1] for r in rows]
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(months, revenue, color=BLUE, linewidth=2, marker="o", markersize=3)
    ax.set_title("Monthly Revenue (Feb 2023 - Dec 2024)", loc="left", fontsize=13)
    ax.yaxis.set_major_formatter(FuncFormatter(money))
    ax.set_xticks(months[::3])
    ax.tick_params(axis="x", rotation=45)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(IMAGES_DIR, "monthly_revenue.png"), dpi=150)
    plt.close(fig)

    # Chart 2: revenue by category (query 3)
    _, rows = results[3]
    bar_chart([r[0] for r in rows], [r[3] for r in rows],
              "Revenue by Category", "Revenue",
              os.path.join(IMAGES_DIR, "revenue_by_category.png"))

    # Chart 3: return rate by payment method (query 5)
    _, rows = results[5]
    bar_chart([r[0] for r in rows], [r[3] for r in rows],
              "Return Rate by Payment Method", "Return rate",
              os.path.join(IMAGES_DIR, "return_rate_by_payment.png"),
              fmt=lambda x, _p=None: f"{x:.1f}%")

    # Chart 4: revenue per customer by region (query 6)
    _, rows = results[6]
    rows = sorted(rows, key=lambda r: r[3], reverse=True)
    bar_chart([r[0] for r in rows], [r[3] for r in rows],
              "Revenue per Customer by Region", "Revenue per customer",
              os.path.join(IMAGES_DIR, "revenue_per_customer_by_region.png"),
              fmt=lambda x, _p=None: f"${x:,.0f}")

    conn.close()
    print(f"Charts saved to {IMAGES_DIR}/")


if __name__ == "__main__":
    main()
