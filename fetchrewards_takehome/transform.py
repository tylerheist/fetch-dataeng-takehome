"""Functions related to the transformation layer in this take home's ETL process."""
import pandas as pd
from cryptography.fernet import Fernet
from utils import COLUMNS_TO_MASK


def transform_user_login_data(df: pd.DataFrame, ekey: bytes) -> pd.DataFrame:
    """transforms user login data to have masked fields and also conform to DDL given.

    Args:
        df (pd.DataFrame): input dataframe from extract process (SQS queue polling)
        ekey (bytes): key used for fernet encrpytion

    Returns:
        pd.DataFrame: output dataframe with transformed fields (new masked columns,
            overridden type conversion, and new date field)
    """
    fernet_encrypter = Fernet(ekey)
    for col in COLUMNS_TO_MASK:
        df["masked_" + col] = (
            df[col]
            .apply(str.encode)
            .apply(fernet_encrypter.encrypt)
            .apply(bytes.decode)
        )
    # Assumption: UTC is ok
    df["create_date"] = pd.to_datetime(df["SentTimestamp"], unit="s").dt.date
    # so the ddl shows this as an integer, but it's clearly using
    # semantic versioning - not sure what the best approach would be
    # Assumption: that combining the major, minor, and patch version
    # numbers will result in something reasonable and intelligible
    df["app_version"] = pd.to_numeric(
        df["app_version"].str.replace(".", "", regex=False)
    )
    return df
