import pandas as pd


df = pd.read_csv("./datasource/v2.csv", parse_dates=["timeStamp"], low_memory=False)


force_string_cols = ["tripID", "deviceID", "dtc"]

for col in force_string_cols:
    df[col] = df[col].astype(str)


numeric_cols = ["accData", "gps_speed", "battery", "cTemp", "eLoad", "iat", "imap", "kpl", "maf", "rpm", "speed", "tAdv", "tPos"]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")


df.to_parquet("./datasource/v2.parquet", index=False)

print("✅ CSV successfully converted to Parquet!")
