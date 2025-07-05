CLEAN_PATH = "s3://aditya-bucket-processed/vehicle_health/"
AGG_PATH   = "s3://aditya-bucket-aggregated/vehicle_health_agg/"

from pyspark.context import SparkContext
from pyspark.sql import functions as F
from awsglue.context import GlueContext

sc          = SparkContext()
glueContext = GlueContext(sc)
spark       = glueContext.spark_session


df = spark.read.parquet(CLEAN_PATH)
print("RAW rows :", df.count())


df = (df
       .withColumn("rpm",          F.col("rpm").cast("double"))
       .withColumn("engine_load",  F.col("eLoad").cast("double"))
       .withColumn("coolant_temp", F.col("cTemp").cast("double"))
)


df_agg = (df
    .withColumn("date", F.to_date("timeStamp"))
    .groupBy("deviceID", "date")
    .agg(
        F.avg("rpm").alias("avg_rpm"),
        F.max("rpm").alias("max_rpm"),
        F.avg("engine_load").alias("avg_engine_load"),
        F.max("coolant_temp").alias("max_coolant_temp"),
        F.count("*").alias("records")
    )
)

print("AGG rows :", df_agg.count())


(df_agg.write
     .mode("overwrite")                 
     .partitionBy("date", "deviceID")   
     .parquet(AGG_PATH))

print(f"Aggregated parquet written → {AGG_PATH}")