from db import get_connection
import json

# ---------- HELPER ----------
def load_jsonl(path):
    with open("../" + path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

# ---------- DB CONNECTION ----------
conn = get_connection()
cursor = conn.cursor()

# ---------- CREATE TABLES ----------
cursor.executescript("""
CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    name TEXT
);

CREATE TABLE IF NOT EXISTS sales_orders (
    sales_order_id TEXT PRIMARY KEY,
    customer_id TEXT,
    total_amount REAL
);

CREATE TABLE IF NOT EXISTS sales_order_items (
    sales_order_id TEXT,
    item_id TEXT,
    product_id TEXT,
    amount REAL
);

CREATE TABLE IF NOT EXISTS deliveries (
    delivery_id TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS delivery_items (
    delivery_id TEXT,
    sales_order_id TEXT
);

CREATE TABLE IF NOT EXISTS billing (
    billing_id TEXT PRIMARY KEY,
    customer_id TEXT,
    accounting_id TEXT,
    amount REAL
);

CREATE TABLE IF NOT EXISTS billing_items (
    billing_id TEXT,
    product_id TEXT,
    delivery_id TEXT,
    amount REAL
);

CREATE TABLE IF NOT EXISTS products (
    product_id TEXT PRIMARY KEY,
    name TEXT
);

CREATE TABLE IF NOT EXISTS accounting (
    accounting_id TEXT PRIMARY KEY,
    customer_id TEXT
);

CREATE TABLE IF NOT EXISTS payments (
    accounting_id TEXT,
    amount REAL
);
""")

conn.commit()

# =====================================================
# 🔹 SALES ORDERS (DEDUP FIX)
# =====================================================

data = load_jsonl("data/sales_order_headers.jsonl")

seen = set()
count = 0

for r in data:
    order_id = r.get("salesOrder")

    if not order_id or order_id in seen:
        continue

    seen.add(order_id)

    try:
        cursor.execute("""
            INSERT OR IGNORE INTO sales_orders (sales_order_id, customer_id, total_amount)
            VALUES (?, ?, ?)
        """, (
            order_id,
            r.get("soldToParty"),
            float(r.get("totalNetAmount", 0))
        ))
        count += 1
    except Exception as e:
        print("❌ Sales order error:", e)

print("✅ Sales orders inserted:", count)

# =====================================================
# 🔹 SALES ORDER ITEMS
# =====================================================

data = load_jsonl("data/sales_order_items.jsonl")

count = 0
for r in data:
    try:
        cursor.execute("""
            INSERT INTO sales_order_items VALUES (?, ?, ?, ?)
        """, (
            r.get("salesOrder"),
            r.get("salesOrderItem"),
            r.get("material"),
            float(r.get("netAmount", 0))
        ))
        count += 1
    except Exception as e:
        print("❌ SO item error:", e)

print("✅ Sales order items:", count)

# =====================================================
# 🔹 DELIVERY ITEMS
# =====================================================

data = load_jsonl("data/delivery_items.jsonl")

count = 0
for r in data:
    try:
        cursor.execute("""
            INSERT INTO delivery_items VALUES (?, ?)
        """, (
            r.get("deliveryDocument"),
            r.get("referenceSDDocument")
        ))
        count += 1
    except Exception as e:
        print("❌ Delivery error:", e)

print("✅ Delivery items:", count)

# =====================================================
# 🔹 BILLING (DEDUP FIX)
# =====================================================

data = load_jsonl("data/billing.jsonl")

seen = set()
count = 0

for r in data:
    billing_id = r.get("billingDocument")

    if not billing_id or billing_id in seen:
        continue

    seen.add(billing_id)

    try:
        cursor.execute("""
            INSERT OR IGNORE INTO billing (billing_id, customer_id, accounting_id, amount)
            VALUES (?, ?, ?, ?)
        """, (
            billing_id,
            r.get("soldToParty"),
            r.get("accountingDocument"),
            float(r.get("totalNetAmount", 0))
        ))
        count += 1
    except Exception as e:
        print("❌ Billing error:", e)

print("✅ Billing inserted:", count)

# =====================================================
# 🔹 BILLING ITEMS
# =====================================================

data = load_jsonl("data/billing_items.jsonl")

count = 0
for r in data:
    try:
        cursor.execute("""
            INSERT INTO billing_items VALUES (?, ?, ?, ?)
        """, (
            r.get("billingDocument"),
            r.get("material"),
            r.get("referenceSdDocument"),
            float(r.get("netAmount", 0))
        ))
        count += 1
    except Exception as e:
        print("❌ Billing item error:", e)

print("✅ Billing items:", count)

# =====================================================
# 🔹 PRODUCTS
# =====================================================

data = load_jsonl("data/product_descriptions.jsonl")

count = 0
for r in data:
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO products VALUES (?, ?)
        """, (
            r.get("product"),
            r.get("productDescription")
        ))
        count += 1
    except Exception as e:
        print("❌ Product error:", e)

print("✅ Products:", count)

# =====================================================
# 🔹 CUSTOMERS
# =====================================================

data = load_jsonl("data/customers.jsonl")

count = 0
for r in data:
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO customers VALUES (?, ?)
        """, (
            r.get("customer"),
            r.get("businessPartnerFullName")
        ))
        count += 1
    except Exception as e:
        print("❌ Customer error:", e)

print("✅ Customers:", count)

# =====================================================
# 🔹 PAYMENTS
# =====================================================

data = load_jsonl("data/payments.jsonl")

count = 0
for r in data:
    try:
        cursor.execute("""
            INSERT INTO payments VALUES (?, ?)
        """, (
            r.get("accountingDocument"),
            float(r.get("amount", 0))
        ))
        count += 1
    except Exception as e:
        print("❌ Payment error:", e)

print("✅ Payments:", count)

# ---------- FINAL COMMIT ----------
conn.commit()

# =====================================================
# 🔹 CREATE INDEXES FOR PERFORMANCE
# =====================================================

cursor.executescript("""
CREATE INDEX IF NOT EXISTS idx_billing_id ON billing_items(billing_id);
CREATE INDEX IF NOT EXISTS idx_delivery_id ON delivery_items(delivery_id);
CREATE INDEX IF NOT EXISTS idx_sales_order_id ON sales_orders(sales_order_id);
CREATE INDEX IF NOT EXISTS idx_product_id ON products(product_id);
CREATE INDEX IF NOT EXISTS idx_customer_id ON customers(customer_id);
CREATE INDEX IF NOT EXISTS idx_accounting_id ON payments(accounting_id);
""")

conn.commit()
conn.close()

print("✅ Database indexes created")

print("🚀 DATA LOADING COMPLETE")