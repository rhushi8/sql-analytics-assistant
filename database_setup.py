import sqlite3
import pandas as pd
import random

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Drop old tables
cursor.execute("DROP TABLE IF EXISTS sales")
cursor.execute("DROP TABLE IF EXISTS customers")
cursor.execute("DROP TABLE IF EXISTS products")

# Create customers table
cursor.execute("""
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    customer_name TEXT,
    region TEXT
)
""")

# Create products table
cursor.execute("""
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT,
    category TEXT
)
""")

# Create sales table with foreign keys
cursor.execute("""
CREATE TABLE sales (
    sale_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    product_id INTEGER,
    revenue INTEGER,
    month TEXT,
    FOREIGN KEY(customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY(product_id) REFERENCES products(product_id)
)
""")

# Insert sample customers
regions = ["North", "South", "East", "West"]
customers_data = []

for i in range(1, 8):
    customers_data.append((i, f"Customer_{i}", random.choice(regions)))

cursor.executemany(
    "INSERT INTO customers VALUES (?, ?, ?)",
    customers_data
)

# Insert sample products
categories = ["Electronics", "Mobile", "Accessories"]
products_data = []

for i in range(1, 6):
    products_data.append((i, f"Product_{i}", random.choice(categories)))

cursor.executemany(
    "INSERT INTO products VALUES (?, ?, ?)",
    products_data
)

# Insert sales
months = ["Jan", "Feb", "Mar", "Apr"]
sales_data = []

for i in range(1, 51):
    sales_data.append((
        i,
        random.randint(1, 7),
        random.randint(1, 5),
        random.randint(500, 2000),
        random.choice(months)
    ))

cursor.executemany(
    "INSERT INTO sales VALUES (?, ?, ?, ?, ?)",
    sales_data
)

conn.commit()
conn.close()

print("Multi-table database created successfully!")