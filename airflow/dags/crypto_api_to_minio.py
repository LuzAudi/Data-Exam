import os
import json
import requests
from io import BytesIO
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable

from minio import Minio
from dotenv import load_dotenv

# Upload .env
load_dotenv()

# MinIO Configuration
MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME")
MINIO_ROOT_USER = os.getenv("MINIO_ROOT_USER")
MINIO_ROOT_PASSWORD = os.getenv("MINIO_ROOT_PASSWORD")
#COIN = os.getenv("COIN_ID", "bitcoin")
API_KEY = os.getenv("GECKO_KEY")
HEADERS = {"x-cg-demo-api-key": API_KEY}

# Get the currency name from Airflow Variables
COIN = Variable.get("crypto_coin", default_var="bitcoin")

MINIO_CLIENT = Minio(
    "minio:9000",
    access_key=MINIO_ROOT_USER,
    secret_key=MINIO_ROOT_PASSWORD,
    secure=False,
)

# DAG config
default_args = {
    "owner": "Luz",
    "start_date": datetime.now() - timedelta(days=1),
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

# Create bucket if it doesn't exist
def create_bucket():
    if not MINIO_CLIENT.bucket_exists(MINIO_BUCKET_NAME):
        MINIO_CLIENT.make_bucket(MINIO_BUCKET_NAME)

# Download and upload directly to MinIO
def upload_json_data(**context):
    execution_date = context["ds"]
    formatted_date = datetime.strptime(execution_date, "%Y-%m-%d").strftime("%d-%m-%Y")
    url = f"https://api.coingecko.com/api/v3/coins/{COIN}/history?date={formatted_date}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        raise Exception(f"API error: {response.status_code} - {response.text}")

    json_bytes = BytesIO(response.content)
    object_name = f"{COIN}_{execution_date}.json"

    MINIO_CLIENT.put_object(
        bucket_name=MINIO_BUCKET_NAME,
        object_name=object_name,
        data=json_bytes,
        length=len(response.content),
        content_type="application/json"
    )

    print(f"Uploaded {object_name} to MinIO")

# DAG definition
with DAG(
    dag_id="crypto_api_to_minio_direct",
    default_args=default_args,
    schedule_interval="0 13 * * *",
    catchup=False,
    tags=["crypto", "minio"]
) as dag:

    create_bucket_task = PythonOperator(
        task_id="create_bucket",
        python_callable=create_bucket,
    )

    upload_task = PythonOperator(
        task_id="upload_json_data",
        python_callable=upload_json_data,
        provide_context=True,
    )

    create_bucket_task >> upload_task
