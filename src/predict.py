import os
import joblib
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "aqi_model.pkl")

model = joblib.load(MODEL_PATH)

def predict_aqi(data):
    features = np.array([[
        data["temp"],
        data["humidity"],
        data["wind"],
        data["pressure"],
        data["pm2_5"],
        data["pm10"],
        data["no2"]
    ]])

    return float(model.predict(features)[0])