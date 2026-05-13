from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.predict import predict_aqi
from src.live_data import get_live_data
from datetime import datetime

app = FastAPI(
    title="AQI Intelligence API",
    version="1.0.0",
    description="Real-time AQI Prediction API"
)

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- HOME ----------------
@app.get("/")
def home():
    return {
        "message": "AQI Intelligence API Running",
        "status": "online",
        "timestamp": str(datetime.now())
    }

# ---------------- HEALTH CHECK ----------------
@app.get("/health")
def health():
    return {
        "status": "healthy"
    }

# ---------------- PREDICTION ----------------
@app.get("/predict/{city}")
def predict(city: str):

    data = get_live_data(city)

    if "error" in data:
        raise HTTPException(status_code=400, detail=data["error"])

    aqi = predict_aqi(data)

    return {
        "city": city,
        "predicted_aqi": round(aqi, 2),
        "temperature": data["temp"],
        "humidity": data["humidity"],
        "pm2_5": data["pm2_5"],
        "pm10": data["pm10"],
        "no2": data["no2"],
        "timestamp": str(datetime.now())
    }