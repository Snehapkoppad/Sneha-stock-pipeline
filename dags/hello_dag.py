from airflow import DAG
from airflow.operators.empty import EmptyOperator
from datetime import datetime

with DAG(dag_id="hello_dag", start_date=datetime(2023,1,1), schedule_interval=None, catchup=False) as dag:
    start = EmptyOperator(task_id="start")
