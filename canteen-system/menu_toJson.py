import pandas as pd
import json

# Input and output file paths
input_excel = "menu_items.xlsx"      # your Excel file
output_json = "menu.json"      # output JSON file

# Read Excel file
df = pd.read_excel(input_excel)

# Ensure only required columns are included
df = df[['food', 'price']]

# Convert to list of dictionaries
data = df.to_dict(orient='records')

# Write to JSON file
with open(output_json, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print(f"✅ Successfully converted '{input_excel}' to '{output_json}'")
