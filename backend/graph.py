import sqlite3

def build_graph(highlight=None):
    conn = sqlite3.connect("business.db")
    cursor = conn.cursor()

    nodes = {}
    edges = []

    # ---------- SALES ORDER ----------
    so_rows = cursor.execute("""
        SELECT sales_order_id, customer_id
        FROM sales_orders
        LIMIT 200
    """).fetchall()

    for so, customer in so_rows:
        nodes[so] = {"id": so, "type": "sales_order"}
        nodes[customer] = {"id": customer, "type": "customer"}
        edges.append({"source": customer, "target": so})

    # ---------- DELIVERY ----------
    delivery_rows = cursor.execute("""
        SELECT delivery_id, sales_order_id
        FROM delivery_items
        LIMIT 200
    """).fetchall()

    for delivery, so in delivery_rows:
        nodes[delivery] = {"id": delivery, "type": "delivery"}
        nodes[so] = {"id": so, "type": "sales_order"}
        edges.append({"source": so, "target": delivery})

    # ---------- BILLING ----------
    billing_rows = cursor.execute("""
        SELECT billing_id, delivery_id, product_id
        FROM billing_items
        LIMIT 300
    """).fetchall()

    for bill, delivery, product in billing_rows:
        nodes[bill] = {"id": bill, "type": "billing"}
        nodes[delivery] = {"id": delivery, "type": "delivery"}
        nodes[product] = {"id": product, "type": "product"}
        edges.append({"source": delivery, "target": bill})
        edges.append({"source": bill, "target": product})

    # ---------- PAYMENTS ----------
    payment_rows = cursor.execute("""
        SELECT accounting_id
        FROM payments
        LIMIT 200
    """).fetchall()

    for (acc,) in payment_rows:
        nodes[acc] = {"id": acc, "type": "payment"}

    conn.close()

    # ---------- FORMAT ----------
    node_list = []

    for n in nodes.values():
        if highlight and str(n["id"]) == str(highlight):
            color = "green"
        elif n["type"] == "sales_order":
            color = "blue"
        elif n["type"] == "delivery":
            color = "orange"
        elif n["type"] == "billing":
            color = "red"
        elif n["type"] == "product":
            color = "purple"
        elif n["type"] == "customer":
            color = "#FFB347"
        elif n["type"] == "payment":
            color = "#87CEEB"
        else:
            color = "gray"

        node_list.append({
            "id": str(n["id"]),
            "label": f"{n['type']}: {n['id']}",
            "color": color
        })

    return {"nodes": node_list, "edges": edges}