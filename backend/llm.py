import os
import requests

# ---------- API KEY ----------
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    try:
        import streamlit as st
        api_key = st.secrets.get("GROQ_API_KEY")
    except:
        pass

if not api_key:
    raise ValueError("GROQ_API_KEY not found")

# ---------- GROQ API ----------
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}


# ---------- SYSTEM PROMPT ----------
SYSTEM_PROMPT = """
You are an expert SQL generator for SQLite.

STRICT RULES:
- Only use these exact tables and columns
- Do NOT invent columns
- Always qualify columns when joining

Schema:
sales_orders(sales_order_id, customer_id, total_amount)
sales_order_items(sales_order_id, item_id, product_id, amount)
billing(billing_id, customer_id, accounting_id, amount)
billing_items(billing_id, product_id, delivery_id, amount)
delivery_items(delivery_id, sales_order_id)
payments(accounting_id, amount)

Return ONLY SQL.
"""


# ---------- GENERATE SQL ----------
def generate_sql(user_query):
    try:
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_query}
            ],
            "temperature": 0
        }

        res = requests.post(GROQ_URL, headers=HEADERS, json=payload)
        data = res.json()

        return data["choices"][0]["message"]["content"].strip()

    except Exception as e:
        return f"ERROR: {str(e)}"


# ---------- GENERATE ANSWER ----------
def generate_answer(question, result):
    try:
        prompt = f"""
Explain this result clearly:

Question: {question}
Data: {result}
"""

        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": prompt}],
        }

        res = requests.post(GROQ_URL, headers=HEADERS, json=payload)
        data = res.json()

        return data["choices"][0]["message"]["content"].strip()

    except Exception as e:
        return f"Error: {str(e)}"
