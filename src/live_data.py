import requests
import streamlit as st

# ---------------- API KEY ----------------
API_KEY = st.secrets["OPENWEATHER_API_KEY"]

# ---------------- GET LIVE DATA ----------------
def get_live_data(city):

    try:

        # ---------------- GEO LOCATION API ----------------
        geo_url = (
            f"http://api.openweathermap.org/geo/1.0/direct"
            f"?q={city}&limit=1&appid={API_KEY}"
        )

        geo_response = requests.get(geo_url, timeout=10)

        geo_data = geo_response.json()

        if not geo_data:
            return {
                "error": "City not found"
            }

        lat = geo_data[0]["lat"]
        lon = geo_data[0]["lon"]

        # ---------------- WEATHER API ----------------
        weather_url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        )

        weather_response = requests.get(weather_url, timeout=10)

        weather_data = weather_response.json()

        # ---------------- AIR POLLUTION API ----------------
        pollution_url = (
            f"http://api.openweathermap.org/data/2.5/air_pollution"
            f"?lat={lat}&lon={lon}&appid={API_KEY}"
        )

        pollution_response = requests.get(
            pollution_url,
            timeout=10
        )

        pollution_data = pollution_response.json()

        # ---------------- VALIDATION ----------------
        if "list" not in pollution_data:

            return {
                "error": "Invalid pollution API response"
            }

        components = pollution_data["list"][0]["components"]

        # ---------------- RETURN CLEAN DATA ----------------
        return {

            "city": city,

            "pm2_5": float(components.get("pm2_5", 0)),
            "pm10": float(components.get("pm10", 0)),
            "co": float(components.get("co", 0)),
            "no2": float(components.get("no2", 0)),
            "so2": float(components.get("so2", 0)),
            "o3": float(components.get("o3", 0)),

            "temp": float(weather_data["main"]["temp"]),
            "humidity": float(weather_data["main"]["humidity"]),
            "pressure": float(weather_data["main"]["pressure"]),
            "wind_speed": float(weather_data["wind"]["speed"])
        }

    except Exception as e:

        return {
            "error": str(e)
        }