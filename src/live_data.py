import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")

WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
AIR_URL = "https://api.openweathermap.org/data/2.5/air_pollution"


def get_live_data(city):

    weather_params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    w = requests.get(WEATHER_URL, params=weather_params)

    if w.status_code != 200:
        return {"error": w.text}

    w = w.json()

    lat = w["coord"]["lat"]
    lon = w["coord"]["lon"]

    air_params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY
    }

    a = requests.get(AIR_URL, params=air_params)

    if a.status_code != 200:
        return {"error": a.text}

    a = a.json()["list"][0]["components"]

    return {
        "city": w["name"],
        "temp": w["main"]["temp"],
        "humidity": w["main"]["humidity"],
        "pressure": w["main"]["pressure"],
        "wind": w["wind"]["speed"],
        "weather": w["weather"][0]["description"],

        "pm2_5": a.get("pm2_5", 0),
        "pm10": a.get("pm10", 0),
        "co": a.get("co", 0),
        "no2": a.get("no2", 0),
        "o3": a.get("o3", 0),
        "so2": a.get("so2", 0),
        "nh3": a.get("nh3", 0)
    }