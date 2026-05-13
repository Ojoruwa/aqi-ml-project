import os
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from xgboost import XGBRegressor

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATA_PATH = os.path.join(BASE_DIR, "data", "cleaned", "aqi_data.csv")
MODEL_PATH = os.path.join(BASE_DIR, "models", "aqi_model.pkl")

df = pd.read_csv(DATA_PATH)

features = [
    "temp", "humidity", "wind", "pressure",
    "pm2_5", "pm10", "co", "no2", "o3", "so2", "nh3"
]

target = "aqi"

X = df[features]
y = df[target]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = XGBRegressor(
    n_estimators=400,
    learning_rate=0.05,
    max_depth=6,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)

model.fit(X_train, y_train)

preds = model.predict(X_test)

mae = mean_absolute_error(y_test, preds)
r2 = r2_score(y_test, preds)

print("\n🔥 XGBOOST MODEL RESULTS")
print("MAE:", mae)
print("R2:", r2)

joblib.dump(model, MODEL_PATH)

print("\n✅ Model saved:", MODEL_PATH)