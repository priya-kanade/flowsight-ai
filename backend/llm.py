from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are an expert SQL generator for SQLite.

STRICT RULES:
- Only use these exact tables and columns
- Do NOT invent columns
- Always qualify columns with table names when joining
- Never use ambiguous column names

Schema:

sales_orders(sales_order_id, customer_id, total_amount)

sales_order_items(sales_order_id, item_id, product_id, amount)

billing(billing_id, customer_id, accounting_id, amount)

billing_items(billing_id, product_id, delivery_id, amount)

delivery_items(delivery_id, sales_order_id)

payments(accounting_id, amount)
---

Examples:

Q: total revenue
A: SELECT SUM(amount) FROM billing;

Q: number of orders
A: SELECT COUNT(*) FROM sales_orders;

Q: top 5 products by revenue
A: SELECT product_id, SUM(amount) as revenue 
   FROM billing_items 
   GROUP BY product_id 
   ORDER BY revenue DESC 
   LIMIT 5;

Q: total sales per product
A: SELECT product_id, SUM(amount) 
   FROM billing_items 
   GROUP BY product_id;

---

Rules:
- Use table.column format when needed
- Use SUM(), COUNT() for aggregation
- Return ONLY SQL (no explanation)

Question: {question}
"""

def generate_sql(user_query):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_query}
            ],
            temperature=0
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"ERROR: {str(e)}"
    
def generate_answer(question, result):
    prompt = f"""
You are a senior business analyst AI.

Your job is to explain data insights in a human, conversational way.

- Keep answers concise and to the point
- Be conversational and natural
- Do NOT show raw tuples or brackets
- Highlight key numbers clearly
- If multiple results → summarize briefly
- Sound like ChatGPT, not a report

Question: {question}
Data: {result}

Answer:
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content.strip()
