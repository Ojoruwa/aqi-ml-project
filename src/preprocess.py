import os
import pandas as pd

# -----------------------------
# PATHS
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

RAW_PATH = os.path.join(BASE_DIR, "data", "raw")
CLEAN_PATH = os.path.join(BASE_DIR, "data", "cleaned")


# -----------------------------
# LOAD RAW DATA
# -----------------------------
def load_raw_data():

    files = os.listdir(RAW_PATH)

    csv_files = [f for f in files if f.endswith(".csv")]

    if not csv_files:
        raise Exception("No CSV file found in data/raw")

    file_path = os.path.join(RAW_PATH, csv_files[0])

    print(f"\nLoading dataset:\n{file_path}")

    return pd.read_csv(file_path)


# -----------------------------
# CLEAN DATA
# -----------------------------
def clean_data(df):

    print("\nOriginal Columns:")
    print(df.columns.tolist())

    # lowercase everything
    df.columns = [c.strip().lower() for c in df.columns]

    # Rename important columns
    rename_map = {
        "temperature": "temp",
        "temp": "temp",
        "humidity": "humidity",
        "wind_speed": "wind",
        "windspeed": "wind",
        "wind": "wind",
        "pressure": "pressure",
        "aqi": "aqi",
        "pm2_5": "pm2_5",
        "pm10": "pm10",
        "co": "co",
        "no2": "no2",
        "o3": "o3",
        "so2": "so2",
        "nh3": "nh3"
    }

    df = df.rename(columns=rename_map)

    # KEEP ALL IMPORTANT FEATURES
    required_columns = [
        "temp",
        "humidity",
        "wind",
        "pressure",
        "pm2_5",
        "pm10",
        "co",
        "no2",
        "o3",
        "so2",
        "nh3",
        "aqi"
    ]

    available_columns = [c for c in required_columns if c in df.columns]

    print("\nAvailable ML Columns:")
    print(available_columns)

    missing = [c for c in required_columns if c not in df.columns]

    if missing:
        print("\nMissing Columns:")
        print(missing)

    df = df[available_columns]

    # convert numeric
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # remove bad rows
    df = df.dropna()

    print(f"\nFinal dataset shape: {df.shape}")

    return df


# -----------------------------
# SAVE CLEAN DATA
# -----------------------------
def save_clean_data(df):

    os.makedirs(CLEAN_PATH, exist_ok=True)

    save_path = os.path.join(CLEAN_PATH, "aqi_data.csv")

    df.to_csv(save_path, index=False)

    print(f"\nClean dataset saved to:\n{save_path}")


# -----------------------------
# RUN
# -----------------------------
def run():

    print("Starting preprocessing pipeline...\n")

    df = load_raw_data()

    clean_df = clean_data(df)

    save_clean_data(clean_df)

    print("\n✅ PREPROCESSING COMPLETE")


if __name__ == "__main__":
    run()