"""Functions related to the load layer in this take home's ETL process."""
import pandas as pd
from utils import COLUMNS_TO_LOAD, create_postgres_engine


def load_data_to_postgres(
    df: pd.DataFrame,
    database: str,
    host: str,
    user: str,
    password: str,
    port: str,
    table_name: str,
) -> int:
    """Loads a given dataframe into a given postgres table,
    returning the number of rows written

    Args:
        df (pd.DataFrame): data frame to be written
        database (str): postgres database to write to
        host (str): host info for postgres instance
        user (str): username for postgres instance
        password (str): password for postgres instance
        port (str): port of postgres instance
        table_name (str): table to be written to

    Returns:
        int: number of rows written to postgres
    """
    pg_engine = create_postgres_engine(database, host, user, password, port)
    with pg_engine.connect().execution_options(isolation_level="AUTOCOMMIT") as pg_conn:
        # there is certainly a more efficient and fast way to load the data into 
        # postgres, but this was what I decided on with the time spent.
        # This would be one of the places I would want to come back to, think about,
        # do some research, and re-address.
        rows_written = df[COLUMNS_TO_LOAD].to_sql(
            table_name, con=pg_conn, if_exists="replace", index=False, chunksize=1000
        )
    return rows_written
