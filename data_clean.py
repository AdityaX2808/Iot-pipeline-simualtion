import pandas as pd

# Load parquet with pyarrow
df = pd.read_parquet("./datasource/v2.parquet", engine="pyarrow")

# Clean deviceID column
df["deviceID"] = df["deviceID"].astype(str).str.strip()

# Keep only expected valid IDs
valid_ids = ['0.0', '1.0', '2.0', '3.0', '4.0', '5.0', '6.0', '7.0', '8.0',
             '9.0', '10.0', '11.0', '12.0', '14.0', '16.0']

# Filter: Remove the string "deviceID" and keep only the 15 expected IDs
df = df[(df["deviceID"] != "deviceID") & (df["deviceID"].isin(valid_ids))]

# Save cleaned file
df.to_parquet("./datasource/v2_cleaned.parquet", index=False)

# Display final summary
print("✅ Cleaned and saved!")
print("Remaining deviceIDs:", sorted(df["deviceID"].unique()))
print("Final shape:", df.shape)