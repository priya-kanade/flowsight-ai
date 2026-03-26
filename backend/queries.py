from backend.db import get_connection

def run_sql(sql):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        result = cursor.execute(sql).fetchall()
        columns = [desc[0] for desc in cursor.description]

        return {
            "columns": columns,
            "rows": result
        }

    except Exception as e:
        return {
            "error": str(e),
            "sql": sql
        }