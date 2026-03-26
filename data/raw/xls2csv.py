import pandas as pd
import os
import sys

if len(sys.argv) < 2:
    print("Usage: python xls_to_csv_per_sheet.py input.xlsx [output_folder]")
    sys.exit(1)

input_file = sys.argv[1]
output_dir = sys.argv[2] if len(sys.argv) > 2 else "output_csv"

os.makedirs(output_dir, exist_ok=True)

xls = pd.ExcelFile(input_file)
base_name = os.path.splitext(os.path.basename(input_file))[0]

for sheet in xls.sheet_names:
    df = pd.read_excel(xls, sheet_name=sheet)
    safe_name = sheet.replace(" ", "_").replace("/", "_")
    output_path = os.path.join(output_dir, f"{base_name}_{safe_name}.csv")
    
    df.to_csv(output_path, index=False)
    print(f"Saved: {output_path}")

print("Done!")