## Cryptocurrency Data Engineering Project
This repository contains the complete solution to a 4-part technical data engineering challenge using Python, PostgreSQL, Airflow, and MinIO. The structure and scripts cover data fetching, storage, transformation, and orchestration.

## Project Structure

- `crypto_fetcher/`: Solution to Task 1. Fetches and stores raw data from the CoinGecko API.
- `data/`:
  - `json_results/`: Raw API responses saved as JSON (also used in Task 1).
  - `scripts/`: SQL scripts used for analysis (Task 3).
  - `tables/`: SQL scripts for creating the PostgreSQL schema (Task 2).
- `dags/`: Solution to Task 4. Contains the Airflow DAGs for orchestration and automation.
- `README.md`: Project documentation.

# Task 1 – Data Fetching
Location: crypto_fetcher/

A Python CLI app that fetches data from the CoinGecko API and stores it locally.

Features:

- --daily: fetches the current day's data for a given coin.

- --range: fetches data for a date range.

- --store: inserts the fetched JSON into the PostgreSQL database (coin_raw_data).

- Supports logging, configuration via environment variables, and error handling.

# Task 2 – PostgreSQL Schema
Location: data/tables/

- SQL script to define the schema in PostgreSQL:

  - Table coin_raw_data contains: coin, date, price_usd, and the full API json.
  - Table coin_monthly_aggregates contains: Table coin_monthly_aggregates contains: coin, month, min_price_usd, max_price_usd

- Compatible with Airflow PostgreSQL connection.

- Seed data stored in data/json_results/ was also used in testing Task 1.

# Task 3 – Data Analysis with SQL
Location: data/scripts/

1. Average Price per Coin per Month
Calculates the average price of each cryptocurrency for every month to understand how a coin performed on average during a specific period.

2. Price Increase After Drops
This SQL script calculates how much a coin's price tends to increase after more than 3 consecutive days of price drops. It also includes the most recent market cap.

  Steps:

  1. Identify falling days using LAG().

  2. Group sequences of falling days.

  3. Filter sequences longer than 3 days.

  4. Measure the increase on the next day.

  5. Combine it with the latest market cap per coin.

# Task 4 – Airflow DAGs
Location: dags/

1. DAG 1 – crypto_api_to_minio_direct.py
Automates the fetch of daily price data from CoinGecko and uploads it directly to MinIO as JSON.

- Tasks:

  - create_bucket

  - upload_json_data

- Schedule: Daily at 13:00 UTC

- No intermediate file storage needed.

- Uses Airflow variable crypto_coin for coin selection.

2. DAG 2 – price_chart.py

This DAG waits for the daily record of a selected cryptocurrency to be present in the coin_raw_data table. Once available, it queries the coin_monthly_aggregates table to retrieve the last 30 monthly open/close prices (min/max), generates a plot, and logs the average difference.

- Tasks:
  - wait_for_data: SQL Sensor that waits for the daily record to exist in coin_raw_data
  - analyze_monthly_prices: Python task that:
    - Retrieves max_price and min_price from the coin_monthly_aggregates table
    - Plots open vs. close price (min vs. max)
    - Logs the average difference
    - Saves a plot in /opt/airflow/data/plots/ with the date included in the filename

- Adaptation to Limitation:
  The original requirement asked for daily open and close prices. However, the CoinGecko API only provides one value per day (current_price). To overcome this, we calculate open/close using monthly aggregates and log differences accordingly.

- Triggering:
  You can trigger the DAG manually with custom execution dates thanks to the dummy_param in the params block.

- Requirements:
  - Airflow Variable: crypto_coin (e.g., "bitcoin")
  - Airflow Connection: postgres_conn_id for PostgreSQL access
  - .env: MINIO_ROOT_USER, MINIO_ROOT_PASSWORD, MINIO_BUCKET_NAME
