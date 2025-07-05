import csv
import json

input_csv = r"path\to\csvfile\vehicle.csv"
output_json = r"path\of\json-file\output.json"

with open(input_csv, mode="r", encoding="utf-8") as csv_file, \
     open(output_json, mode="w", encoding="utf-8") as json_file:

    reader = csv.DictReader(csv_file)

    for row in reader:
        json_line = json.dumps(row)
        json_file.write(json_line + "\n")

print("Success")


