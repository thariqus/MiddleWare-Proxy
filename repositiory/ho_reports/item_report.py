from repositiory.database_configuration.mysql_connection import get_connection

def fetch_items(limit=100):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM items LIMIT %s", (limit,))
            return cur.fetchall()
    finally:
        conn.close()