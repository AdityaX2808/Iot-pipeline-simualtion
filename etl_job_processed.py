RAW_DB      = "testdb"
RAW_TABLE   = "aditya_bucket_raw"
PROC_PATH   = "s3://aditya-bucket-processed/vehicle_health/"  


NUMERIC_COLS = [
    "gps_speed", "battery", "cTemp", "dtc", "eLoad",
    "iat", "imap", "kpl", "maf", "rpm", "speed", "tAdv", "tPos"
]

from pyspark.context import SparkContext
from pyspark.sql import functions as F
from awsglue.context import GlueContext

sc          = SparkContext()
glueContext = GlueContext(sc)
spark       = glueContext.spark_session
spark.conf.set("spark.sql.caseSensitive", "false")   


df = (glueContext
        .create_dynamic_frame_from_catalog(database=RAW_DB, table_name=RAW_TABLE)
        .toDF())

print("RAW rows :", df.count())


for col in NUMERIC_COLS:
    if col in df.columns:
        df = df.withColumn(col, F.col(col).cast("double"))


if "timeStamp" in df.columns:
    df = df.withColumn("timeStamp", F.to_timestamp("timeStamp"))


df = df.filter(F.col("tripID").isNotNull() & F.col("deviceID").isNotNull())

print("CLEAN rows:", df.count())


(df.write
     .mode("overwrite")              
     .parquet(PROC_PATH))

print(f"Cleaned data written → {PROC_PATH}")
