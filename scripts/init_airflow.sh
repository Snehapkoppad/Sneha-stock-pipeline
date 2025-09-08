#!/bin/bash
echo "Waiting for Postgres..."
until pg_isready -h postgres -p 5432; do sleep 2; done

echo "Initializing Airflow DB..."
airflow db init

echo "Creating Admin user..."
airflow users create \
    --username admin \
    --password admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com

echo "Airflow initialization finished."
