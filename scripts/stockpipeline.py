# scripts/stockpipeline.py
import os
import requests
import psycopg2
from datetime import datetime

API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")
SYMBOL = os.getenv("STOCK_SYMBOL", "IBM")
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_NAME = os.getenv("DB_NAME", "airflow")
DB_USER = os.getenv("DB_USER", "airflow")
DB_PASS = os.getenv("DB_PASS", "airflow")

def run():
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": SYMBOL,
        "interval": "60min",
        "apikey": API_KEY,
    }

    try:
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()

        ts_key = [k for k in data.keys() if "Time Series" in k]
        if not ts_key:
            print("No time series in response")
            return

        ts = data[ts_key[0]]

        conn = psycopg2.connect(
            host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS
        )
        cur = conn.cursor()

        count = 0
        for t, v in list(ts.items())[:3]:
            dt = datetime.fromisoformat(t)
            cur.execute(
                """
                INSERT INTO stocks (symbol, data_date, open, high, low, close, volume)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT DO NOTHING;
                """,
                (
                    SYMBOL,
                    dt,
                    v["1. open"],
                    v["2. high"],
                    v["3. low"],
                    v["4. close"],
                    v["5. volume"],
                ),
            )
            count += 1
        conn.commit()
        cur.close()
        conn.close()
        print(f"Inserted {count} rows for {SYMBOL}")

    except Exception as e:
        print("Error in stockpipeline.run:", str(e))
        raise