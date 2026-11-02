import os
from dotenv import load_dotenv
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row

load_dotenv()

pool = ConnectionPool(
    conninfo = (
        f"host={os.getenv('DB_HOST')} "
        f"port={os.getenv('DB_PORT', 5432)} "
        f"dbname={os.getenv('DB_NAME')} "
        f"user={os.getenv('DB_USER')} "
        f"password={os.getenv('DB_PASSWORD')}"
    ),
    min_size = 1,
    max_size = 10,
    kwargs={"row_factory": dict_row, "options": "-c search_path=staging"},
)

def get_connection():
    return pool.connection()