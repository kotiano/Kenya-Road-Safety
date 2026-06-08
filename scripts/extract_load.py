import os
import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s")
log = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data" / "raw"

# Snowflake connection
def get_snowflake_connection():
    return snowflake.connector.connect(
        account   = os.environ["SNOWFLAKE_ACCOUNT"],
        user      = os.environ["SNOWFLAKE_USER"],
        password  = os.environ["SNOWFLAKE_PASSWORD"],
        database  = "ROAD_SAFETY",
        schema    = "RAW",
        warehouse = "KENYA_ANALYTICS_WH",
        role      = "TRANSFORMER",
    )

# Cleaning helpers 
def clean_str_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Strip whitespace and title-case string columns."""
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()
    return df

def standardise_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Upper-case column names to match Snowflake convention."""
    df.columns = [c.upper() for c in df.columns]
    return df

# Load CSV 
def load_table(conn, csv_filename: str, table_name: str, drop_cols: list = None):
    path = DATA_DIR / csv_filename
    log.info(f"Reading {path}")
    df = pd.read_csv(path, comment="#")

    if drop_cols:
        df.drop(columns=[c for c in drop_cols if c in df.columns], inplace=True)

    df = clean_str_columns(df)
    df = standardise_columns(df)

    # Remove columns Snowflake table doesn't expect
    success, n_chunks, n_rows, _ = write_pandas(
        conn,
        df,
        table_name.upper(),
        schema="RAW",
        database="ROAD_SAFETY",
        overwrite=True,
        auto_create_table=False,
    )
    if success:
        log.info(f"✓ Loaded {n_rows} rows → RAW.{table_name.upper()}")
    else:
        log.error(f"✗ Failed to load {table_name}")

def main():
    log.info("Connecting to Snowflake…")
    conn = get_snowflake_connection()

    load_table(conn, "ntsa_annual_fatalities.csv",    "ANNUAL_FATALITIES",    drop_cols=["source"])
    load_table(conn, "ntsa_road_user_fatalities.csv", "ROAD_USER_FATALITIES", drop_cols=["notes"])
    load_table(conn, "ntsa_accident_causes.csv",      "ACCIDENT_CAUSES",      drop_cols=["notes"])
    load_table(conn, "ntsa_monthly_2024.csv",         "MONTHLY_FATALITIES",   drop_cols=["source"])
    load_table(conn, "ntsa_hotspot_roads.csv",        "HOTSPOT_ROADS",        drop_cols=["notes"])
    load_table(conn, "ntsa_county_data.csv",          "COUNTY_DATA",          drop_cols=["notes"])

    conn.close()
    log.info("All tables loaded.")

if __name__ == "__main__":
    main()
