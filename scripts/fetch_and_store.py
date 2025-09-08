import requests
import psycopg2
from datetime import datetime

# Alpha Vantage API URL
URL = "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=IBM&interval=5min&apikey=demo"

# PostgreSQL config
DB_HOST = "postgres"  # Use service name from docker-compose
DB_NAME = "stockdb"
DB_USER = "airflow"
DB_PASSWORD = "airflow"

def fetch_data():
    print("Fetching stock data...")
    response = requests.get(URL)
    response.raise_for_status()  # Raise error if request fails
    data = response.json()
    return data["Time Series (5min)"]

def store_data(time_series):
    print("Storing stock data into PostgreSQL...")
    conn = psycopg2.connect(
        host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )
    cur = conn.cursor()

    # Create table if not exists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS stock_data (
            timestamp TIMESTAMP PRIMARY KEY,
            open NUMERIC,
            high NUMERIC,
            low NUMERIC,
            close NUMERIC,
            volume BIGINT
        );
    """)

    for ts, values in time_series.items():
        cur.execute("""
            INSERT INTO stock_data (timestamp, open, high, low, close, volume)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (timestamp) DO NOTHING;
        """, (
            datetime.strptime(ts, "%Y-%m-%d %H:%M:%S"),
            float(values["1. open"]),
            float(values["2. high"]),
            float(values["3. low"]),
            float(values["4. close"]),
            int(values["5. volume"])
        ))

    conn.commit()
    cur.close()
    conn.close()
    print("Done.")

if __name__ == "__main__":
    try:
        ts_data = fetch_data()
        store_data(ts_data)
    except Exception as e:
        print("Error:", e)
