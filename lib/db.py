import os
import psycopg2
from psycopg2.extras import execute_values
from typing import List, Dict

DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_NAME = os.getenv("POSTGRES_DB", "stocks")
DB_USER = os.getenv("POSTGRES_USER", "airflow")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "airflow")
DB_PORT = int(os.getenv("POSTGRES_PORT", 5432))

def _get_conn():
    return psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS, port=DB_PORT)

def upsert_quotes(rows: List[Dict]):
    """
    rows: list of dicts with keys: symbol, ts, open, high, low, close, volume
    """
    if not rows:
        return

    values = [
        (r["symbol"], r["ts"], r["open"], r["high"], r["low"], r["close"], r["volume"])
        for r in rows
    ]

    sql = """
    INSERT INTO stock_quotes (symbol, ts, open, high, low, close, volume)
    VALUES %s
    ON CONFLICT (symbol, ts) DO UPDATE SET
      open = EXCLUDED.open,
      high = EXCLUDED.high,
      low = EXCLUDED.low,
      close = EXCLUDED.close,
      volume = EXCLUDED.volume;
    """

    conn = _get_conn()
    try:
        with conn:
            with conn.cursor() as cur:
                execute_values(cur, sql, values)
    finally:
        conn.close()
