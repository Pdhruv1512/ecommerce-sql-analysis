"""
Generates a synthetic e-commerce dataset and loads it into a SQLite database
(ecommerce.db) so the SQL business-analysis project has real, queryable data.
No external APIs/downloads required -- fully self-contained and reproducible.
"""
import sqlite3
import random
import datetime

random.seed(42)

DB_PATH = "ecommerce.db"

FIRST_NAMES = ["James","Maria","John","Aisha","Wei","Carlos","Priya","Emma","Liam",
               "Sofia","Noah","Fatima","Ethan","Olivia","Mateo","Ananya","Lucas",
               "Chloe","Ravi","Grace","Daniel","Layla","Mason","Zoe","Arjun",
               "Isabella","Kevin","Nadia","Tyler","Hannah"]
LAST_NAMES = ["Smith","Johnson","Garcia","Patel","Chen","Rodriguez","Kumar","Brown",
              "Nguyen","Kim","Ali","Davis","Martinez","Singh","Wilson","Lopez",
              "Anderson","Khan","Taylor","Moore"]

CATEGORIES = ["Electronics","Home & Kitchen","Sports & Outdoors","Books",
              "Clothing","Beauty","Toys","Office Supplies"]

PRODUCTS = {
    "Electronics": ["Wireless Earbuds","Bluetooth Speaker","Phone Charger","Laptop Stand",
                    "USB-C Hub","Smartwatch","Webcam","Mechanical Keyboard"],
    "Home & Kitchen": ["Air Fryer","Coffee Maker","Blender","Cutting Board Set",
                       "Knife Set","Toaster","Vacuum Cleaner","Storage Bins"],
    "Sports & Outdoors": ["Yoga Mat","Water Bottle","Resistance Bands","Camping Tent",
                          "Hiking Backpack","Dumbbell Set","Bike Helmet","Running Shoes"],
    "Books": ["Mystery Novel","Cookbook","Self-Help Guide","Sci-Fi Novel",
              "Business Book","Children's Book","History Book","Biography"],
    "Clothing": ["Cotton T-Shirt","Denim Jeans","Winter Jacket","Running Shorts",
                 "Wool Sweater","Rain Jacket","Baseball Cap","Socks (3-pack)"],
    "Beauty": ["Face Moisturizer","Shampoo","Sunscreen SPF50","Lip Balm Set",
               "Hair Dryer","Makeup Brush Set","Perfume","Face Mask Set"],
    "Toys": ["Building Blocks Set","Puzzle 1000pc","Remote Control Car","Board Game",
             "Action Figure","Plush Toy","Art Supply Kit","Toy Drone"],
    "Office Supplies": ["Notebook Pack","Desk Organizer","Stapler","Pen Set",
                        "Sticky Notes","Whiteboard","File Folders","Desk Lamp"],
}

REGIONS = ["Northeast","Southeast","Midwest","Southwest","West"]
PAYMENT_METHODS = ["Credit Card","Debit Card","PayPal","Gift Card"]

def build():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.executescript("""
    DROP TABLE IF EXISTS order_items;
    DROP TABLE IF EXISTS orders;
    DROP TABLE IF EXISTS products;
    DROP TABLE IF EXISTS customers;

    CREATE TABLE customers (
        customer_id INTEGER PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        region TEXT,
        signup_date TEXT
    );

    CREATE TABLE products (
        product_id INTEGER PRIMARY KEY,
        product_name TEXT,
        category TEXT,
        unit_price REAL
    );

    CREATE TABLE orders (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        order_date TEXT,
        payment_method TEXT,
        is_returned INTEGER,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    );

    CREATE TABLE order_items (
        order_item_id INTEGER PRIMARY KEY,
        order_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        FOREIGN KEY (order_id) REFERENCES orders(order_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    );
    """)

    # --- customers ---
    start = datetime.date(2023, 1, 1)
    end = datetime.date(2024, 12, 1)
    n_customers = 800
    customers = []
    for cid in range(1, n_customers + 1):
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        region = random.choice(REGIONS)
        days_range = (end - start).days
        signup = start + datetime.timedelta(days=random.randint(0, days_range))
        customers.append((cid, fn, ln, region, signup.isoformat()))
    cur.executemany("INSERT INTO customers VALUES (?,?,?,?,?)", customers)

    # --- products ---
    products = []
    pid = 1
    for cat, items in PRODUCTS.items():
        for name in items:
            price = round(random.uniform(8, 250), 2)
            products.append((pid, name, cat, price))
            pid += 1
    cur.executemany("INSERT INTO products VALUES (?,?,?,?)", products)
    product_ids = [p[0] for p in products]

    # --- orders + order_items ---
    order_id = 1
    order_item_id = 1
    orders = []
    order_items = []
    end_order_date = datetime.date(2024, 12, 31)

    for cid, _, _, _, signup_str in customers:
        signup = datetime.date.fromisoformat(signup_str)
        # number of orders per customer -- skewed so some customers buy a lot, most buy a little
        n_orders = max(0, int(random.gammavariate(2, 1.3)))
        for _ in range(n_orders):
            days_after_signup = (end_order_date - signup).days
            if days_after_signup <= 0:
                continue
            order_date = signup + datetime.timedelta(days=random.randint(0, days_after_signup))
            payment = random.choice(PAYMENT_METHODS)
            is_returned = 1 if random.random() < 0.06 else 0
            orders.append((order_id, cid, order_date.isoformat(), payment, is_returned))

            n_items = random.randint(1, 4)
            chosen = random.sample(product_ids, n_items)
            for prod_id in chosen:
                qty = random.randint(1, 3)
                order_items.append((order_item_id, order_id, prod_id, qty))
                order_item_id += 1

            order_id += 1

    cur.executemany("INSERT INTO orders VALUES (?,?,?,?,?)", orders)
    cur.executemany("INSERT INTO order_items VALUES (?,?,?,?)", order_items)

    conn.commit()
    print(f"customers: {len(customers)}")
    print(f"products:  {len(products)}")
    print(f"orders:    {len(orders)}")
    print(f"order_items: {len(order_items)}")
    conn.close()

if __name__ == "__main__":
    build()
