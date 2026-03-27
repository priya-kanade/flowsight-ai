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
        so = str(so)
        customer = str(customer)

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
        delivery = str(delivery)
        so = str(so)

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
        bill = str(bill)
        delivery = str(delivery)
        product = str(product)

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
        acc = str(acc)
        nodes[acc] = {"id": acc, "type": "payment"}

    conn.close()

    # ---------- FORMAT ----------
    node_list = []

    for n in nodes.values():
        node_id = str(n["id"])

        if highlight and node_id == str(highlight):
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
            "id": node_id,
            "label": f"{n['type']}: {node_id}",
            "color": color
        })

    # 🔥 DEBUG (can remove later)
    print("Nodes:", len(node_list))
    print("Edges:", len(edges))

    return {"nodes": node_list, "edges": edges}