import os
import sys
import json
import pandas as pd
import streamlit as st
from datetime import datetime

import plotly.graph_objects as go
import pydeck as pdk

from streamlit_autorefresh import st_autorefresh

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(BASE_DIR)

from src.predict import predict_aqi
from src.live_data import get_live_data

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="AQI Intelligence Platform",
    page_icon="🌍",
    layout="wide"
)

# Auto refresh every 60 seconds
st_autorefresh(interval=60000, key="aqi_refresh")

# ---------------- UI STYLE ----------------
st.markdown("""
<style>
.main { background-color: #0e1117; }
h1, h2, h3 { color: #4dd0e1; }
div[data-testid="metric-container"] {
    background-color: #1c1f26;
    padding: 15px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.title("🌍 AQI Intelligence Platform")
st.caption("Real-time Air Quality Monitoring + ML Insights")

# ---------------- INPUT ----------------
city = st.text_input("Enter City", "Lagos")

with st.spinner("Fetching live data..."):
    data = get_live_data(city)

if "error" in data:
    st.error(data["error"])
    st.stop()

# ---------------- PREDICTION ----------------
aqi = predict_aqi(data)

def aqi_status(aqi):
    if aqi <= 50:
        return "Good", "🟢"
    elif aqi <= 100:
        return "Moderate", "🟡"
    elif aqi <= 150:
        return "Unhealthy", "🟠"
    return "Hazardous", "🔴"

status, icon = aqi_status(aqi)

# ---------------- ALERT SYSTEM ----------------
st.markdown("## 🚨 Air Quality Status")

if aqi > 150:
    st.error(f"{icon} Hazardous Air Quality - Stay Indoors")
elif aqi > 100:
    st.warning(f"{icon} Unhealthy Air Quality - Limit Outdoor Activity")
elif aqi > 50:
    st.info(f"{icon} Moderate Air Quality")
else:
    st.success(f"{icon} Good Air Quality")

# ---------------- METRICS ----------------
st.markdown("## 📊 Live Metrics")

c1, c2, c3, c4 = st.columns(4)

c1.metric("City", data["city"])
c2.metric("Temperature", f"{data['temp']} °C")
c3.metric("Humidity", f"{data['humidity']}%")
c4.metric("AQI", f"{aqi:.2f}")

# ---------------- POLLUTION ----------------
st.markdown("## 🌫 Pollutants")

p1, p2, p3 = st.columns(3)
p1.metric("PM2.5", data["pm2_5"])
p2.metric("PM10", data["pm10"])
p3.metric("NO2", data["no2"])

# ---------------- HISTORY ----------------
HISTORY_FILE = os.path.join(BASE_DIR, "aqi_history.json")

def load_history():
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_history(h):
    with open(HISTORY_FILE, "w") as f:
        json.dump(h, f)

def update_history(value):
    h = load_history()
    h.append({"time": datetime.now().strftime("%H:%M"), "aqi": float(value)})
    h = h[-24:]
    save_history(h)
    return h

history = update_history(aqi)

# ---------------- TREND GRAPH ----------------
st.markdown("## 📈 AQI Trend (24h)")

df = pd.DataFrame(history)

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
st.markdown("## 🔮 Simple Forecast")

if len(df) >= 5:
    trend = df["aqi"].tail(5).mean()
    st.write({
        "Next 1 step": round(trend * 1.02, 2),
        "Next 2 steps": round(trend * 1.05, 2),
        "Next 3 steps": round(trend * 1.08, 2)
    })
else:
    st.info("Collecting data for forecast...")

# ---------------- HEATMAP ----------------
st.markdown("## 🗺 AQI Heatmap")

cities = {
    "Lagos": [6.5244, 3.3792],
    "Abuja": [9.0765, 7.3986],
    "Ibadan": [7.3775, 3.9470],
    "London": [51.5072, -0.1276]
}

heat_data = []

for c, (lat, lon) in cities.items():
    d = get_live_data(c)
    if "error" not in d:
        v = predict_aqi(d)
        heat_data.append([lat, lon, v])

df_map = pd.DataFrame(heat_data, columns=["lat", "lon", "aqi"])

layer = pdk.Layer(
    "HeatmapLayer",
    data=df_map,
    get_position=["lon", "lat"],
    get_weight="aqi",
    radiusPixels=60
)

view_state = pdk.ViewState(
    latitude=6.5,
    longitude=3.3,
    zoom=3
)

st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state))

# ---------------- CITY COMPARISON ----------------
st.markdown("## 🌍 City Comparison")

cols = st.columns(len(cities))

for i, c in enumerate(cities.keys()):
    d = get_live_data(c)
    if "error" not in d:
        v = predict_aqi(d)
        cols[i].metric(c, f"{v:.1f}")