from airflow import DAG
from airflow.providers.common.sql.sensors.sql import SqlSensor
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime, timedelta
from airflow.models.param import Param
import pandas as pd
import matplotlib.pyplot as plt
import os
from sqlalchemy import create_engine

default_args = {
    "owner": "Luz",
    "retries": 1,
    "retry_delay": timedelta(minutes=5)
}

def plot_monthly_aggregates(**context):
    coin = Variable.get("crypto_coin")
    conn_str = "postgresql+psycopg2://airflow:airflow@postgres:5432/airflow"
    engine = create_engine(conn_str)

    query = f"""
        SELECT year, month, max_price, min_price
        FROM coin_monthly_aggregates
        WHERE coin = '{coin}'
        ORDER BY year DESC, month DESC
        LIMIT 30;
    """

    df = pd.read_sql(query, con=engine)
    df["open"] = df["min_price"]
    df["close"] = df["max_price"]
    df["diff"] = df["close"] - df["open"]
    df["label"] = df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2)

    plt.figure(figsize=(10, 5))
    plt.plot(df["label"], df["open"], marker='o', label="Open Price")
    plt.plot(df["label"], df["close"], marker='x', label="Close Price")
    plt.title(f"{coin.capitalize()} - Open/Close Monthly Prices (Last 30 records)")
    plt.xlabel("Month")
    plt.ylabel("Price (USD)")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()

    os.makedirs("/opt/airflow/data/plots", exist_ok=True)
    today = datetime.today().strftime("%Y%m%d")
    file_path = f"/opt/airflow/data/plots/{coin}_open_close_monthly_{today}.png"
    plt.tight_layout()
    plt.savefig(file_path)
    print(f"Saved plot to {file_path}")

    avg_diff = df["diff"].mean()
    print(f"Average monthly open-close difference: {avg_diff:.2f} USD")

with DAG(
    dag_id="price_chart",
    default_args=default_args,
    params={"dummy_param": Param(5, type="integer", minimum=3)},
    start_date=datetime(2024, 1, 1),
    schedule_interval="0 13 * * *", 
    catchup=False,
    tags=["crypto"]
) as dag:

    wait_for_data = SqlSensor(
        task_id="wait_for_data",
        conn_id="postgres_conn_id",
        sql="""
            SELECT 1 FROM coin_raw_data
            WHERE coin = '{{ var.value.crypto_coin }}'
              AND date = '{{ ds }}'
            LIMIT 1;
        """,
        mode="poke",
        poke_interval=30,
        timeout=60 * 5
    )

    analyze_monthly_data = PythonOperator(
        task_id="analyze_monthly_prices",
        python_callable=plot_monthly_aggregates
    )

    wait_for_data >> analyze_monthly_data
