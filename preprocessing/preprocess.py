import pandas as pd
import os

# --- Step 1: Load dataset ---
csv_path = 'data.csv'
if not os.path.exists(csv_path):
    raise FileNotFoundError(f"CSV file not found at {csv_path}. "
                            "Please place it in the preprocessing folder.")

df = pd.read_csv(csv_path, low_memory=False)

# --- Step 2: Clean column names ---
df.columns = [col.strip().replace(" ", "_") for col in df.columns]

# --- Step 3: Convert Admin_No → privilege_level ---
admin_col = None
for col in df.columns:
    if col.lower() == "admin_no".lower():
        admin_col = col
        break

if admin_col is None:
    print("Warning: 'Admin_No' column not found. All users will be set as normal privilege.")
    df["privilege_level"] = 1
else:
    df["privilege_level"] = df[admin_col].map({
        True: 5,
        False: 1,
        "TRUE": 5,
        "FALSE": 1
    })
    df["privilege_level"] = df["privilege_level"].fillna(1)

# --- Step 4: Convert TRUE/FALSE strings to 1/0 ---
bool_map = {"TRUE": 1, "FALSE": 0, True: 1, False: 0}

for col in df.columns:
    if df[col].dtype == object:
        df[col] = df[col].replace(bool_map)

# --- Step 5: Convert mixed-type columns ---
for col in df.columns:
    if df[col].dtype == object:
        try:
            df[col] = pd.to_numeric(df[col])
        except ValueError:
            df[col] = df[col].astype("category")  # fallback to categorical

# --- Step 6: Handle missing values ---
for col in df.columns:
    if pd.api.types.is_numeric_dtype(df[col]):
        median_val = df[col].median()
        df[col] = df[col].fillna(median_val)
    elif pd.api.types.is_categorical_dtype(df[col]) or df[col].dtype == object:
        mode_val = df[col].mode()
        if not mode_val.empty:
            df[col] = df[col].fillna(mode_val[0])
        else:
            df[col] = df[col].fillna("Unknown")  # fallback

# --- Step 7: Create anomaly labels ---
if "Anomaly" in df.columns:
    df["label"] = (df["Anomaly"] != "None").astype(int)
elif "Mitigation" in df.columns:
    df["label"] = (df["Mitigation"] != "None").astype(int)
else:
    df["label"] = 0  # safe default

# --- Step 8: Save cleaned dataset ---
output_path = "../datasets/data_cleaned.csv"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
df.to_csv(output_path, index=False)

print(f"Preprocessing complete → saved as {output_path}")
print(df.head())
print("\nData types after preprocessing:")
print(df.dtypes)
