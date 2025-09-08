import requests
import psycopg2
import os

def run():
    """
    Fetch stock data from API and insert into PostgreSQL table.
    """

    # Example API (replace with real stock API)
    url = "https://dummyjson.com/products?limit=5"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data: {response.status_code}")

    data = response.json().get("products", [])

    # Database connection settings (from environment variables)
    db_host = os.getenv("POSTGRES_HOST", "postgres")
    db_name = os.getenv("POSTGRES_DB", "airflow")
    db_user = os.getenv("POSTGRES_USER", "airflow")
    db_pass = os.getenv("POSTGRES_PASSWORD", "airflow")

    conn = psycopg2.connect(
        host=db_host,
        dbname=db_name,
        user=db_user,
        password=db_pass
    )
    cur = conn.cursor()

    # Create table if not exists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS stocks (
            id SERIAL PRIMARY KEY,
            stock_id INT,
            title TEXT,
            price NUMERIC,
            brand TEXT
        )
    """)

    # Insert each stock item
    for item in data:
        cur.execute("""
            INSERT INTO stocks (stock_id, title, price, brand)
            VALUES (%s, %s, %s, %s)
        """, (
            item.get("id"),
            item.get("title"),
            item.get("price"),
            item.get("brand")
        ))

    conn.commit()
    cur.close()
    conn.close()

    print("Data inserted into PostgreSQL successfully ✅")
