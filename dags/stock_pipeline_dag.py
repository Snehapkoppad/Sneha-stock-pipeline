from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import psycopg2

# DAG default args
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Function to fetch stock data and store in Postgres
def fetch_and_store():
    API_URL = "https://www.alphavantage.co/query"
    API_KEY = "demo"  # replace with your own key
    SYMBOL = "IBM"

    # Fetch data
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": SYMBOL,
        "interval": "5min",
        "apikey": API_KEY
    }
    response = requests.get(API_URL, params=params)
    data = response.json()

    # Parse data
    time_series = data.get("Time Series (5min)", {})
    rows = []
    for time, values in time_series.items():
        rows.append((
            time,
            float(values['1. open']),
            float(values['2. high']),
            float(values['3. low']),
            float(values['4. close']),
            int(values['5. volume'])
        ))

    # Store in Postgres
    conn = psycopg2.connect(
        host="postgres",
        database="stockdb",
        user="airflow",
        password="airflow"
    )
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS stock_data (
            timestamp TIMESTAMP PRIMARY KEY,
            open FLOAT,
            high FLOAT,
            low FLOAT,
            close FLOAT,
            volume BIGINT
        )
    """)
    for row in rows:
        cur.execute("""
            INSERT INTO stock_data (timestamp, open, high, low, close, volume)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (timestamp) DO NOTHING
        """, row)
    conn.commit()
    cur.close()
    conn.close()

# DAG definition
with DAG(
    'stock_pipeline_dag',
    default_args=default_args,
    description='Fetch stock data and store in Postgres',
    schedule_interval='@hourly',
    start_date=datetime(2025, 9, 8),
    catchup=False
) as dag:

    fetch_task = PythonOperator(
        task_id='fetch_and_store',
        python_callable=fetch_and_store
    )
