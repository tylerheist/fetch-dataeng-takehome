"""Functions related to the extract layer in this take home's ETL process."""
import json

import pandas as pd
from utils import get_sqs_client


def extract_user_login_behavior(queue_url: str) -> pd.DataFrame:
    """Extract user login behavior data from SQS queue.

    Args:
        queue_url (str): url that the SQS queue to be ingested from exists at

    Returns:
        pd.DataFrame: data frame containing data of interest from SQS messages.
    """
    all_messages = []
    sqs_client = get_sqs_client()
    while True:
        latest_pull = sqs_client.receive_message(
            QueueUrl=queue_url,
            AttributeNames=["SentTimestamp"],
            VisibilityTimeout=10,
            MaxNumberOfMessages=10,
        ).get("Messages")
        if latest_pull is None or len(latest_pull) == 0:
            break
        all_messages.extend(latest_pull)
    return parse_messages(all_messages)


def parse_messages(list_of_messages: list) -> pd.DataFrame:
    """Parses out fields of interest from json-encoded data.

    Args:
        list_of_messages (list): list of json-encoded data from SQS to be parsed.

    Returns:
        pd.DataFrame: data frame containing data of interest
            parsed out from SQS messages.
    """
    parsed_messages = []
    for message in list_of_messages:
        parsed_message = {}
        parsed_message["ReceiptHandle"] = message.get("ReceiptHandle")
        parsed_message["SentTimestamp"] = message.get("Attributes").get("SentTimestamp")

        body = json.loads(message["Body"])
        if "user_id" not in body.keys():
            # any "faulty" messages that might not fall into the expected set
            # Assumption: that it's ok to not address any message
            # that fall outside the described schema
            # Another assumption: that there might not be other schemas
            # that contain 'user_id' but not the other
            # fields of interest
            continue
        parsed_message = parsed_message | body
        parsed_messages.append(parsed_message)
    return pd.DataFrame.from_dict(parsed_messages)
