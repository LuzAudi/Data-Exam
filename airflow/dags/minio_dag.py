import os
from minio import Minio

from airflow.models import DAG
from airflow.operators.python import PythonOperator

from datetime import datetime, timedelta

START_DATE = datetime.now() - timedelta(days=100)


def create_minio_bucket():
    MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME")
    MINIO_ROOT_USER = os.getenv("MINIO_ROOT_USER")
    MINIO_ROOT_PASSWORD = os.getenv("MINIO_ROOT_PASSWORD")
    print(f"Bucket name is: {MINIO_BUCKET_NAME}")

    client = Minio(
        "minio:9000",
        access_key=MINIO_ROOT_USER,
        secret_key=MINIO_ROOT_PASSWORD,
        secure=False,
    )

    # Make MINIO_BUCKET_NAME if not exist.
    found = client.bucket_exists(MINIO_BUCKET_NAME)
    if not found:
        client.make_bucket(MINIO_BUCKET_NAME)
    else:
        print(f"Bucket '{MINIO_BUCKET_NAME}' already exists!")


default_args = {"owner": "mutt", "retries": 0, "start_date": START_DATE}
with DAG("stock_to_parquet", default_args=default_args, schedule="0 4 * * *"):
    build_minio_bucket = PythonOperator(
        task_id="build_minio_bucket", python_callable=create_minio_bucket
    )
