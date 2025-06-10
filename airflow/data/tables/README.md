# How to Load The Tables into Docker PostgreSQL

1. Copy SQL files into the running container:

docker cp data/coin_raw_data.sql airflow-postgres-1:/coin_raw_data.sql
docker cp data/coin_monthly_aggregates.sql airflow-postgres-1:/coin_monthly_aggregates.sql

2. Enter the container:

docker exec -it airflow-postgres-1 bash

3. Launch the PostgreSQL client:

psql -U airflow -d airflow

4. Execute the SQL files:

\i /coin_raw_data.sql
\i /coin_monthly_aggregates.sql

5. List tables to verify:

\dt

---

# Insert and Update Logic from Python

When the CLI is run with the '--store' flag:

- It inserts a new row in coin_raw_data for each coin and date.
- If a row already exists, it does not insert duplicates (via ON CONFLICT DO NOTHING).
- It then recalculates the monthly max/min for that coin using a GROUP BY and updates (via ON CONFLICT DO UPDATE) the coin_monthly_aggregates table.

---

# Verifying the PostgreSQL Tables

After running the script with --store, you can check that the data has been inserted correctly into the database.

Enter the Postgres container:

docker exec -it airflow-postgres-1 bash
psql -U airflow -d airflow

Check data in coin_raw_data and coin_monthly_aggregates:

SELECT * FROM coin_raw_data ORDER BY date DESC LIMIT 10;
SELECT coin, date, price FROM coin_raw_data ORDER BY date DESC;

SELECT * FROM coin_monthly_aggregates ORDER BY year DESC, month DESC;