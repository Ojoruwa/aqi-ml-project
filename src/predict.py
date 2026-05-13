import os
import joblib

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "aqi_model.pkl")

model = joblib.load(MODEL_PATH)


def predict_aqi(data):

    features = [[
        data["temp"],
        data["humidity"],
        data["wind"],
        data["pressure"],
        data["pm2_5"],
        data["pm10"],
        data["co"],
        data["no2"],
        data["o3"],
        data["so2"],
        data["nh3"]
    ]]

    return float(model.predict(features)[0])