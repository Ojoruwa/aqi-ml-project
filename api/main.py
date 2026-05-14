from fastapi import FastAPI
from src.predict import predict_aqi

app = FastAPI()


@app.get("/")
def home():
    return {
        "message": "AQI ML API Running"
    }


@app.get("/predict")
def predict(
    pm2_5: float,
    pm10: float,
    co: float,
    no2: float,
    o3: float,
    so2: float,
    nh3: float
):
    prediction = predict_aqi(
        pm2_5,
        pm10,
        co,
        no2,
        o3,
        so2,
        nh3
    )

    return {
        "predicted_aqi": prediction
    }