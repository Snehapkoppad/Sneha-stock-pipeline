# Dockerized Stock Data Pipeline (Airflow + Postgres)

## Overview
This project implements a Dockerized pipeline using Apache Airflow to fetch intraday stock quotes from Alpha Vantage and store them in a Postgres DB.

## Prerequisites
- Docker Desktop installed & running
- Docker Compose (v2) available
- Alpha Vantage API key (free tier)

## Setup
1. Clone repo and `cd` into it.
2. Create `.env` (see sample in project).
3. Build & run:
   ```bash
   docker compose down
   docker compose build --no-cache
   docker compose up -d
   docker compose ps
   docker compose logs -f airflow-webserver

