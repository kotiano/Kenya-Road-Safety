import sys
import snowflake.connector
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.context import SparkContext
from pyspark.sql import functions as F
from pyspark.sql.types import IntegerType
from snowflake.connector.pandas_tools import write_pandas

args = getResolvedOptions(sys.argv, [
    "JOB_NAME",
    "S3_INPUT_PATH",
    "SNOWFLAKE_ACCOUNT",
    "SNOWFLAKE_USER",
    "SNOWFLAKE_PASSWORD",
    "SNOWFLAKE_DATABASE",
    "SNOWFLAKE_SCHEMA",
    "SNOWFLAKE_WAREHOUSE",
])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

S3_PATH = args["S3_INPUT_PATH"] 

# Snowflake connection
def get_conn():
    return snowflake.connector.connect(
        account=args["SNOWFLAKE_ACCOUNT"],
        user=args["SNOWFLAKE_USER"],
        password=args["SNOWFLAKE_PASSWORD"],
        database=args["SNOWFLAKE_DATABASE"],
        schema=args["SNOWFLAKE_SCHEMA"],
        warehouse=args["SNOWFLAKE_WAREHOUSE"],
    )


# Helpers
def read_csv(filename: str):
    """Read a CSV from S3 into a Spark DataFrame."""
    return spark.read.option("header", True).option("inferSchema", True).csv(
        f"{S3_PATH}{filename}"
    )


def spark_to_pandas_clean(sdf):
    """Convert Spark DF to pandas, upper-case columns for Snowflake."""
    pdf = sdf.toPandas()
    pdf.columns = [c.upper() for c in pdf.columns]
    # Strip whitespace from string columns
    for col in pdf.select_dtypes(include="object").columns:
        pdf[col] = pdf[col].str.strip()
    return pdf


def load_to_snowflake(pdf, table_name: str, conn):
    success, n_chunks, n_rows, _ = write_pandas(
        conn,
        pdf,
        table_name.upper(),
        overwrite=True,
        auto_create_table=False,
    )
    status = "OK" if success else "FAILED"
    print(f"  [{status}] {table_name} — {n_rows} rows")


# Table definitions
TABLES = [
    ("ntsa_annual_fatalities.csv",    "ANNUAL_FATALITIES"),
    ("ntsa_road_user_fatalities.csv", "ROAD_USER_FATALITIES"),
    ("ntsa_accident_causes.csv",      "ACCIDENT_CAUSES"),
    ("ntsa_monthly_2024.csv",         "MONTHLY_FATALITIES"),
    ("ntsa_hotspot_roads.csv",        "HOTSPOT_ROADS"),
    ("ntsa_county_data.csv",          "COUNTY_DATA"),
]

print(f"\nStarting NTSA raw load from {S3_PATH}")
conn = get_conn()

for csv_file, table in TABLES:
    print(f"\nProcessing {csv_file}")
    try:
        sdf = read_csv(csv_file)

        # Standardise county name casing where column exists
        if "county" in [c.lower() for c in sdf.columns]:
            sdf = sdf.withColumn("county", F.initcap(F.trim(F.col("county"))))

        pdf = spark_to_pandas_clean(sdf)
        # Drop comment/source columns not in Snowflake table definition
        for drop_col in ["SOURCE", "NOTES"]:
            if drop_col in pdf.columns:
                pdf.drop(columns=[drop_col], inplace=True)

        load_to_snowflake(pdf, table, conn)

    except Exception as e:
        print(f"  ERROR on {csv_file}: {e}")
        raise

conn.close()
job.commit()
print("\nGlue job complete.")
