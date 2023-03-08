import os
from configparser import ConfigParser
from pathlib import Path

import localstack_client.session as boto3
from sqlalchemy import create_engine

os.environ["AWS_PROFILE"] = "localstack"
COLUMNS_TO_MASK = ["ip", "device_id"]
COLUMNS_TO_LOAD = [
    "user_id",
    "device_type",
    "masked_ip",
    "masked_device_id",
    "locale",
    "app_version",
    "create_date",
]
CONFIG_PATH = Path(__file__).parent / "config.ini"
SQS_CLIENT = boto3.client("sqs")


def read_config() -> ConfigParser:
    """Open and read the config.

    Returns:
        config parser with contents of the local config.ini
    """
    config = ConfigParser()
    config.read(str(CONFIG_PATH))
    return config


def get_sqs_client():
    return SQS_CLIENT


def create_postgres_engine(
    database: str, host: str, user: str, password: str, port: str
):
    conn_string = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
    return create_engine(conn_string)


def delete_sqs_messages(queue_url: str, list_of_receipt_handles: list) -> list:
    unsuccessful_handles = []
    for item in list_of_receipt_handles:
        response = SQS_CLIENT.delete_message(QueueUrl=queue_url, ReceiptHandle=item)
        if response["ResponseMetadata"]["HTTPStatusCode"] >= 400:
            unsuccessful_handles.append(item)
    return unsuccessful_handles
