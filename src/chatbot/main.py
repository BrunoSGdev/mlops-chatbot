from google import genai
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
import os
import time
import re

# =========================================================
# API Config
# =========================================================
load_dotenv()  # loads variables from .env
api_key = os.getenv("GEMINI_API_KEY")
print(f"[INFO] Loaded GEMINI_API_KEY: {'Yes' if api_key else 'No'}")


client = genai.Client(api_key=api_key)
chat = client.chats.create(model="gemini-2.5-flash")

# =========================================================
# Loading data files
# =========================================================
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "processed"

FILES = {
    "df_input": DATA_DIR / "input_metrics_processed.csv",
    "df_orders": DATA_DIR / "orders_metrics_processed.csv",
    "df_summary": DATA_DIR / "summary_processed.csv"
}
def load_data(files_dict):
    dataframes = {}
    for name, path in files_dict.items():
        if not path.exists():
            raise FileNotFoundError(f"Missing file: {path}")
        print(f"[INFO] Loading {name} from {path}")
        dataframes[name] = pd.read_csv(path)
    return dataframes

dfs = load_data(FILES)


# =========================================================
# SCHEMA GENERATION
# =========================================================
def get_schema(dfs):
    schema = []
    for name, df in dfs.items():
        schema.append(f"{name} columns: {list(df.columns)}")
    return "\n".join(schema)

# =========================================================
# SAFETY FILTER
# =========================================================
FORBIDDEN_PATTERNS = [
    "__",
    "open(",
    "exec(",
    "eval(",
    "os.",
    "sys.",
    "import" 
]

def is_safe(code: str) -> bool:
    if "import pandas as pd" in code:
        code = code.replace("import pandas as pd", "")
    return not any(pattern in code for pattern in FORBIDDEN_PATTERNS)

# =========================================================
# DATASET PARSER
# =========================================================
def parse_dataset(user_input: str):
    user_input = user_input.strip()

    if ":" not in user_input:
        return None, user_input

    prefix, query = user_input.split(":", 1)
    dataset = prefix.strip().lower()
    query = query.strip()

    if dataset not in ["df_input", "df_orders"]:
        return None, user_input

    return dataset, query

# =========================================================
# CLEAN CODE BLOCK
# =========================================================
def clean_code(code: str) -> str:
    return code.replace("```python", "").replace("```", "").strip()

# =========================================================
# GENERATE CODE FROM LLM
# =========================================================
def generate_code(user_input: str, schema: str) -> str:
    df_name, clean_query = parse_dataset(user_input)

    if df_name is None:
        print("[WARNING] No dataset specified. Defaulting to df_input.")
        df_name = "df_input"
        clean_query = user_input

    print(f"[ROUTER] Using: {df_name}")

    prompt = f"""
You are a senior Python data analyst.

You have the following pandas DataFrames:
- df_input
- df_orders

You MUST use ONLY {df_name}.
Do NOT use any other dataframe.

Schema:
{schema}

Write ONLY valid Python pandas code to answer the question.

STRICT RULES:
- Do NOT explain anything
- Do NOT use print()
- Only import pandas as pd
- Store the final result in a variable called result
- Use only pandas operations
- Assume data is already loaded and clean (NaN = 0)
- Do NOT rename columns
- NEVER use another dataframe

- Valid metrics(for the METRIC column use exactly only the following names):
Retail SST > SS CVR, Restaurants SST > SS CVR, Gross Profit UE,
Restaurants SS > ATC CVR, Non-Pro PTC > OP,
% PRO Users Who Breakeven, Pro Adoption (Last Week Status),
MLTV Top Verticals Adoption, % Restaurants Sessions With Optimal Assortment,
Lead Penetration, Restaurants Markdowns / GMV,
Perfect Orders, Turbo Adoption.

- If the user metric is not exact, use the closest one from the list above.

Question:
{clean_query}
"""

    response = chat.send_message(prompt)
    return clean_code(response.text)

# =========================================================
# EXECUTE CODE SAFELY
# =========================================================
def run_code(code: str, dfs: dict):
    local_vars = dict(dfs)

    try:
        exec(code, {}, local_vars)
        return local_vars.get("result", "No result returned")
    except Exception as e:
        return f"[ERROR] Execution failed: {e}"

# =========================================================
# EXPLAIN RESULT
# =========================================================
def explain_result(result):
    prompt = f"""
You are a data analyst.

Explain the following result clearly and concisely:

{result}
"""
    response = chat.send_message(prompt)
    return response.text

# =========================================================
# MAIN LOOP
# =========================================================
def main():
    print("""
Data Analyst Chatbot Ready (type 'endchat' to exit)

You must specify dataset:
- df_input: your question
- df_orders: your question

Example:
df_orders: average orders by city
""")

    schema = get_schema(dfs)

    while True:
        user_input = input("User: ")

        if user_input.lower() == "endchat":
            print("Ending session")
            break

        # Step 1: Generate code
        code = generate_code(user_input, schema)
        print("\n[DEBUG] Generated code:\n", code)

        # Step 2: Safety check
        if not is_safe(code):
            print("[WARNING] Unsafe code detected. Skipping execution.")
            continue

        # Step 3: Execute
        result = run_code(code, dfs)
        print("\n[RESULT]\n", result)

        # Step 4: Explain
        explanation = explain_result(result)
        print("\nDatabot:", explanation)

# =========================================================
# ENTRYPOINT
# =========================================================
if __name__ == "__main__":
    main()