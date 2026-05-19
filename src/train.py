import pandas as pd
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

# -----------------------------
# LOAD DATA
# -----------------------------
DATA_PATH = "data/cleaned/cleaned_aqi.csv"

df = pd.read_csv(DATA_PATH)

print("\nDataset Loaded Successfully")
print(df.head())

# -----------------------------
# FEATURES
# -----------------------------
features = [
    "pm10",
    "co",
    "no2",
    "so2",
    "o3",
    "temp",
    "humidity",
    "pressure",
    "wind_speed"
]

# -----------------------------
# SCIENTIFIC AQI TARGET
# -----------------------------
def classify_aqi(pm25):

    if pm25 <= 12:
        return 0  # Good

    elif pm25 <= 35.4:
        return 1  # Moderate

    elif pm25 <= 55.4:
        return 2  # Unhealthy Sensitive

    elif pm25 <= 150.4:
        return 3  # Unhealthy

    else:
        return 4  # Hazardous

# -----------------------------
# CREATE TARGET
# -----------------------------
df["AQI_Risk"] = df["pm2_5"].apply(classify_aqi)

print("\nAQI Distribution:")
print(df["AQI_Risk"].value_counts())

# -----------------------------
# INPUT / TARGET
# -----------------------------
X = df[features]
y = df["AQI_Risk"]

# -----------------------------
# SPLIT
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# -----------------------------
# SCALE
# -----------------------------
scaler = StandardScaler()

X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# -----------------------------
# MODEL
# -----------------------------
model = RandomForestClassifier(
    n_estimators=150,
    max_depth=12,
    class_weight="balanced",
    random_state=42
)

# -----------------------------
# TRAIN
# -----------------------------
print("\nTraining AQI Model...")

model.fit(X_train, y_train)

# -----------------------------
# EVALUATE
# -----------------------------
preds = model.predict(X_test)

print("\nClassification Report:")
print(classification_report(y_test, preds))

# -----------------------------
# CREATE MODELS FOLDER
# -----------------------------
os.makedirs("models", exist_ok=True)

# -----------------------------
# SAVE MODEL
# -----------------------------
package = {
    "model": model,
    "scaler": scaler,
    "features": features
}

MODEL_PATH = "models/aqi_model.pkl"

joblib.dump(package, MODEL_PATH)

print(f"\nModel saved successfully at: {MODEL_PATH}")