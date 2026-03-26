from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from functools import lru_cache
import time

from backend.graph import build_graph
from backend.llm import generate_sql, generate_answer
from backend.utils import extract_id

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple cache for graph (expires every 2 minutes)
_graph_cache = {"data": None, "timestamp": 0}
_CACHE_TTL = 120  # 2 minutes

def get_cached_graph(highlight=None):
    global _graph_cache
    current_time = time.time()
    
    # Return cached graph if still valid and highlight matches
    if (current_time - _graph_cache["timestamp"] < _CACHE_TTL and 
        _graph_cache["data"] is not None and 
        highlight is None):
        return _graph_cache["data"]
    
    # Rebuild graph
    graph = build_graph(highlight)
    
    # Cache it if no highlight
    if highlight is None:
        _graph_cache["data"] = graph
        _graph_cache["timestamp"] = current_time
    
    return graph


# ---------- ROOT ----------
@app.get("/")
def root():
    return {"message": "FlowSight AI Backend Running"}


# ---------- GRAPH ----------
@app.get("/graph")
def graph(highlight: str = None):
    return get_cached_graph(highlight)


# ---------- TRACE FLOW ----------
def trace_billing_flow(billing_id):
    conn = sqlite3.connect("business.db")
    cursor = conn.cursor()

    result = cursor.execute("""
        SELECT 
            COALESCE(di.sales_order_id, 'Not Linked') as sales_order_id,
            bi.delivery_id,
            bi.billing_id
        FROM billing_items bi
        LEFT JOIN delivery_items di 
        ON bi.delivery_id = di.delivery_id
        WHERE bi.billing_id = ?
    """, (billing_id,)).fetchall()

    return result


# ---------- ASK ----------

@app.get("/ask")
def ask(question: str):

    question_lower = question.lower()

    # ---------- GUARDRAILS ----------
    allowed_keywords = [
        "sales", "billing", "delivery", "product",
        "customer", "payment", "order", "revenue", "flow"
    ]

    if not any(word in question_lower for word in allowed_keywords):
        return {
            "answer": "This system is designed to answer questions related to the dataset only."
        }

    # ---------- TRACE FLOW ----------
    if "trace" in question_lower and "billing" in question_lower:
        billing_id = extract_id(question)

        if not billing_id:
            return {"answer": "Please provide a valid billing ID."}

        conn = sqlite3.connect("business.db")
        cursor = conn.cursor()

        flow = cursor.execute("""
            SELECT 
                COALESCE(di.sales_order_id, 'Not Linked'),
                bi.delivery_id,
                bi.billing_id
            FROM billing_items bi
            LEFT JOIN delivery_items di 
            ON bi.delivery_id = di.delivery_id
            WHERE bi.billing_id = ?
        """, (billing_id,)).fetchall()

        if flow:
            so, delivery, billing = flow[0]

            if so == "Not Linked":
                answer = (
                    f"Delivery {delivery} leads to Billing {billing}, "
                    f"but no linked Sales Order was found in the dataset."
                )
            else:
                answer = (
                    f"Here’s the complete flow:\n\n"
                    f"Sales Order {so} → Delivery {delivery} → Billing {billing}"
                )

            return {
                "answer": answer,
                "highlight": billing_id
            }
        else:
            return {
                "answer": "No flow found for this billing document."
            }

    # ---------- BROKEN FLOW ----------
    if "broken" in question_lower or "incomplete" in question_lower:
        conn = sqlite3.connect("business.db")
        cursor = conn.cursor()

        result = cursor.execute("""
            SELECT sales_order_id
            FROM sales_orders
            WHERE sales_order_id NOT IN (
                SELECT sales_order_id FROM delivery_items
            )
            LIMIT 10
        """).fetchall()

        return {
            "answer": f"Found {len(result)} sales orders with incomplete flow."
        }

    # ---------- NORMAL QUERY ----------
    sql = generate_sql(question)

    conn = sqlite3.connect("business.db")
    cursor = conn.cursor()

    try:
        result = cursor.execute(sql).fetchall()
    except Exception as e:
        return {
            "answer": f"Query failed: {str(e)}"
        }

    # ---------- GENERATE ANSWER ----------
    answer = generate_answer(question, result)

    # ---------- HIGHLIGHT ----------
    highlight = extract_id(question)

    return {
        "answer": answer,
        "highlight": highlight
    }

@app.get("/node/{node_id}")
def get_node(node_id: str):
    conn = sqlite3.connect("business.db")
    cursor = conn.cursor()

    # Single optimized query using UNION - checks all tables at once
    row = cursor.execute("""
        SELECT 'Billing', billing_id, delivery_id, product_id, amount FROM billing_items WHERE billing_id = ?
        UNION ALL
        SELECT 'Delivery', delivery_id, sales_order_id, NULL, NULL FROM delivery_items WHERE delivery_id = ?
        UNION ALL
        SELECT 'Sales Order', sales_order_id, customer_id, NULL, total_amount FROM sales_orders WHERE sales_order_id = ?
        UNION ALL
        SELECT 'Product', product_id, NULL, NULL, NULL FROM products WHERE product_id = ?
        UNION ALL
        SELECT 'Customer', customer_id, NULL, NULL, NULL FROM customers WHERE customer_id = ?
        UNION ALL
        SELECT 'Payment', accounting_id, NULL, NULL, amount FROM payments WHERE accounting_id = ?
        LIMIT 1
    """, (node_id, node_id, node_id, node_id, node_id, node_id)).fetchone()

    conn.close()

    if not row:
        return {"type": "Unknown", "id": node_id}

    node_type = row[0]

    if node_type == "Billing":
        return {"type": "Billing", "billing_id": row[1], "delivery_id": row[2], "product_id": row[3], "amount": row[4]}
    elif node_type == "Delivery":
        return {"type": "Delivery", "delivery_id": row[1], "sales_order_id": row[2]}
    elif node_type == "Sales Order":
        return {"type": "Sales Order", "sales_order_id": row[1], "customer_id": row[2], "amount": row[4]}
    elif node_type == "Product":
        return {"type": "Product", "product_id": row[1]}
    elif node_type == "Customer":
        return {"type": "Customer", "customer_id": row[1]}
    elif node_type == "Payment":
        return {"type": "Payment", "accounting_id": row[1], "amount": row[4]}

    return {"type": "Unknown", "id": node_id}