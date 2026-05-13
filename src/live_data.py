import requests
import time

API_KEY = "YOUR_API_KEY"

WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
AIR_URL = "https://api.openweathermap.org/data/2.5/air_pollution"

# ---------------- SIMPLE CACHE ----------------
_cache = {}
CACHE_TTL = 60  # seconds


def get_live_data(city):

    now = time.time()

    # ---------- RETURN FROM CACHE ----------
    if city in _cache:
        cached_time, cached_data = _cache[city]
        if now - cached_time < CACHE_TTL:
            return cached_data

    try:
        # ---------------- WEATHER ----------------
        weather_params = {
            "q": city,
            "appid": API_KEY,
            "units": "metric"
        }

        weather = requests.get(
            WEATHER_URL,
            params=weather_params,
            timeout=6
        ).json()

        if "coord" not in weather:
            return {"error": "Invalid weather response"}

        lat = weather["coord"]["lat"]
        lon = weather["coord"]["lon"]

        # ---------------- AIR POLLUTION ----------------
        air_params = {
            "lat": lat,
            "lon": lon,
            "appid": API_KEY
        }

        air = requests.get(
            AIR_URL,
            params=air_params,
            timeout=6
        ).json()

        result = {
            "city": city,
            "lat": lat,
            "lon": lon,
            "temp": weather["main"]["temp"],
            "humidity": weather["main"]["humidity"],
            "pm2_5": air["list"][0]["components"]["pm2_5"],
            "pm10": air["list"][0]["components"]["pm10"],
            "no2": air["list"][0]["components"]["no2"]
        }

        # SAVE TO CACHE
        _cache[city] = (now, result)

        return result

    except requests.exceptions.Timeout:
        return {"error": "API timeout — try again"}

    except Exception as e:
        return {"error": str(e)}