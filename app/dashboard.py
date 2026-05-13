import os
import sys
import json
import time
import pandas as pd
import streamlit as st
from datetime import datetime
import plotly.graph_objects as go
import pydeck as pdk

# ---------------- PATH FIX ----------------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(BASE_DIR)

from src.predict import predict_aqi
from src.live_data import get_live_data

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="AQI Intelligence System",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 AQI Intelligence System")
st.caption("Real-time Air Quality Monitoring + ML Insights")

city = st.text_input("Enter City", "Lagos")

# ---------------- HISTORY FILE ----------------
HISTORY_FILE = os.path.join(BASE_DIR, "aqi_history.json")


def load_history():
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def save_history(data):
    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f)


def update_history(value):
    data = load_history()
    data.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "aqi": float(value)
    })
    data = data[-24:]
    save_history(data)
    return data


# ---------------- STATUS ----------------
def aqi_status(aqi):
    if aqi <= 50:
        return "Good", "🟢"
    elif aqi <= 100:
        return "Moderate", "🟡"
    elif aqi <= 150:
        return "Unhealthy", "🟠"
    return "Hazardous", "🔴"


# ---------------- CITY COORDS ----------------
CITIES = {
    "Lagos": [6.5244, 3.3792],
    "Abuja": [9.0765, 7.3986],
    "Ibadan": [7.3775, 3.9470],
    "London": [51.5072, -0.1276],
    "New York": [40.7128, -74.0060]
}


# ---------------- MAIN LOOP ----------------
placeholder = st.empty()

while True:
    with placeholder.container():

        data = get_live_data(city)

        if "error" in data:
            st.error(data["error"])
            break

        aqi = predict_aqi(data)
        status, icon = aqi_status(aqi)

        # ---------------- ALERT ----------------
        if aqi > 150:
            st.error(f"{icon} Hazardous Air Quality")
        elif aqi > 100:
            st.warning(f"{icon} Unhealthy Air Quality")
        elif aqi > 50:
            st.info(f"{icon} Moderate Air Quality")
        else:
            st.success(f"{icon} Good Air Quality")

        # ---------------- METRICS ----------------
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("City", data["city"])
        c2.metric("Temp", f"{data['temp']} °C")
        c3.metric("Humidity", f"{data['humidity']}%")
        c4.metric("AQI", f"{aqi:.2f}")

        # ---------------- POLLUTION ----------------
        st.markdown("## 🌫 Pollutants")

        p1, p2, p3 = st.columns(3)
        p1.metric("PM2.5", data["pm2_5"])
        p2.metric("PM10", data["pm10"])
        p3.metric("NO2", data["no2"])

        # ---------------- HISTORY ----------------
        history = update_history(aqi)
        df = pd.DataFrame(history)

        # ---------------- GRAPH ----------------
        st.markdown("## 📈 AQI Trend")

        if len(df) > 1:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df["time"],
                y=df["aqi"],
                mode="lines+markers"
            ))
            fig.update_layout(template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

        # ---------------- FORECAST ----------------
        st.markdown("## 🔮 Forecast")

        if len(df) >= 5:
            avg = df["aqi"].tail(5).mean()
            st.write({
                "Next 1 step": round(avg * 1.02, 2),
                "Next 2 steps": round(avg * 1.05, 2),
                "Next 3 steps": round(avg * 1.08, 2)
            })
        else:
            st.info("Collecting data...")

        # ---------------- HEATMAP (OPTIMIZED) ----------------
        st.markdown("## 🗺 AQI Heatmap")

        heat_data = []

        for c, (lat, lon) in CITIES.items():
            d = get_live_data(c)

            if "error" not in d:
                heat_data.append([
                    lat,
                    lon,
                    float(d["pm2_5"])
                ])

        df_map = pd.DataFrame(heat_data, columns=["lat", "lon", "value"])

        if not df_map.empty:
            layer = pdk.Layer(
                "HeatmapLayer",
                data=df_map,
                get_position=["lon", "lat"],
                get_weight="value",
                radiusPixels=60
            )

            view_state = pdk.ViewState(
                latitude=6.5,
                longitude=3.3,
                zoom=2.5
            )

            st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state))

    time.sleep(5)