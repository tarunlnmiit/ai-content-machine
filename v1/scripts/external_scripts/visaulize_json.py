import ollama
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import traceback
import re

# ----------------------------
# CONFIG
# ----------------------------
DATA_PATH = "/Users/tarungupta/Making It Big/Claude/content-machine/data/analytics/twitter_tweets.json"
DEFAULT_MODEL = "llama3"

# ----------------------------
# LOAD JSON DATA
# ----------------------------
def load_json_to_df(path):
    with open(path, "r") as f:
        data = json.load(f)

    if isinstance(data, list):
        df = pd.json_normalize(data)

    elif isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, list):
                print(f"🔍 Using nested key: {key}")
                df = pd.json_normalize(value)
                break
        else:
            df = pd.json_normalize(data)

    else:
        raise ValueError("Unsupported JSON format")

    return df


df = load_json_to_df(DATA_PATH)

print("\n✅ Data Loaded:")
print(df.head())

# ✅ REAL COUNT (important fix)
print(f"\n📊 Total rows loaded: {len(df)}")

print("\n📊 Columns:", df.columns.tolist())
print("\n📊 Column Types:\n", df.dtypes)

# ----------------------------
# LIST & SELECT MODEL
# ----------------------------
def list_models():
    models = ollama.list()

    if not models or "models" not in models or models["models"] is None:
        return []

    return [
        m.get("model") or m.get("name")
        for m in models["models"]
        if m.get("model") or m.get("name")
    ]

available_models = list_models()

if not available_models:
    raise RuntimeError("❌ No Ollama models found. Run `ollama pull llama3` first.")

print("\n🤖 Available Models:\n")
for idx, m in enumerate(available_models, 1):
    print(f"{idx}. {m}")

print("\n💡 Suggestions:")
print("- Code-heavy tasks → codellama")
print("- General analysis → llama3")
print("- Fast/light → mistral")

while True:
    try:
        choice = input(f"\nSelect a model [1-{len(available_models)}] (default 1): ").strip()

        if choice == "":
            model = available_models[0]
            break

        choice = int(choice)

        if 1 <= choice <= len(available_models):
            model = available_models[choice - 1]
            break
        else:
            print("⚠️ Invalid number. Try again.")

    except ValueError:
        print("⚠️ Enter a valid number.")

print(f"\n✅ Using model: {model}")

# ----------------------------
# USER QUERY
# ----------------------------
user_query = input("\n📊 What do you want to analyze?\n> ")

# ----------------------------
# PROMPT (FIXED)
# ----------------------------
prompt = f"""
You are a data analyst.

The pandas DataFrame is called df.

Columns:
{df.columns.tolist()}

Column Types:
{df.dtypes.to_dict()}

User request:
{user_query}

Rules:
- Use pandas, matplotlib, seaborn
- df is already loaded
- Handle missing values carefully:
  - Only fill numeric columns with 0
  - Do NOT apply fillna(0) to entire dataframe
- Always include at least one visualization
- Return ONLY executable Python code
- Do not include markdown formatting
"""

# ----------------------------
# CALL OLLAMA
# ----------------------------
print("\n⚡ Generating analysis...\n")

response = ollama.chat(
    model=model,
    messages=[{"role": "user", "content": prompt}]
)

raw_code = response['message']['content']

# ----------------------------
# CLEAN CODE
# ----------------------------
def clean_code(code):
    code = re.sub(r"```.*?\n", "", code)
    code = re.sub(r"```", "", code)
    return code.strip()

code = clean_code(raw_code)

print("🧾 Generated Code:\n")
print(code)

# ----------------------------
# EXECUTE CODE (SAFE CONTEXT)
# ----------------------------
def execute_code(code, df):
    local_vars = {
        "df": df,
        "plt": plt,
        "sns": sns,
        "pd": pd
    }

    try:
        exec(code, {}, local_vars)
        plt.show()
    except Exception:
        print("\n❌ Error executing generated code:")
        traceback.print_exc()

# ----------------------------
# RUN
# ----------------------------
execute_code(code, df)