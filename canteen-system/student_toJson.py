import pandas as pd
import json

# Input and output file paths
input_excel = "student_cards.xlsx"      # your Excel file
output_json = "students.json"      # output JSON file

# Read Excel file
df = pd.read_excel(input_excel)

# Ensure only required columns are included
df = df[['rfid_card_id', 'balance']]

# Convert to list of dictionaries
data = df.to_dict(orient='records')

# Write to JSON file
with open(output_json, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print(f"✅ Successfully converted '{input_excel}' to '{output_json}'")
