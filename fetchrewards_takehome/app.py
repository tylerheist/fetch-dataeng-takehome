import os
import pickle
from configparser import ConfigParser

import pandas as pd
from extract import extract_user_login_behavior
from load import load_data_to_postgres
from transform import transform_user_login_data
from utils import delete_sqs_messages, read_config


def handler():
    """Main function handler"""
    environment = os.environ.get("ENVIRONMENT", "DEV")
    # Read in config
    config: ConfigParser = read_config()
    # call a function from extract that will return a dataframe
    # with all the flattened json data from sqs
    parsed_user_login_data: pd.DataFrame = extract_user_login_behavior(
        config[environment]["queue_url"]
    )
    print(f"{parsed_user_login_data.shape[0]} new records have been extracted")
    # call a function from transform that will mask columns
    # given as parameters and return the transformed dataframe
    transformed_data: pd.DataFrame = transform_user_login_data(
        parsed_user_login_data, config[environment]["fernet_key"].encode()
    )
    print(f"{transformed_data.shape[0]} records have been transformed")
    # call a function that will write with pandas.to_sql() to postgres
    rows_added: int = load_data_to_postgres(
        transformed_data,
        config[environment]["postgres_database"],
        config[environment]["postgres_host"],
        config[environment]["postgres_user"],
        config[environment]["postgres_password"],
        config[environment]["postgres_port"],
        config[environment]["table_name"],
    )
    print(f"{rows_added} rows have been loaded into postgres")
    # call a function that will delete messages from sqs queue after we're done with ETL
    # Assumption: that I'm the only consumer of the SQS queue
    # and it's ok for me to delete the messages rather than
    # baking in some other form of duplicate detection during this process
    unsuccessful_deletes = delete_sqs_messages(
        config[environment]["queue_url"], transformed_data["ReceiptHandle"].tolist()
    )
    print(
        f"{transformed_data.shape[0] - len(unsuccessful_deletes)} messages "
        "have been cleared from the SQS queue"
    )
    if len(unsuccessful_deletes) > 0:
        with open("unsuccessful_sqs_deletes", "wb") as fp:
            pickle.dump(unsuccessful_deletes, fp)
    return


if __name__ == "__main__":
    handler()
