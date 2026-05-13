import os
import sys
import json
import pandas as pd
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
import plotly.graph_objects as go

# -----------------------------
# ROOT PATH FIX
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(BASE_DIR)

from src.predict import predict_aqi
from src.live_data import get_live_data

load_dotenv()

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="AQI Intelligence System",
    page_icon="🌍",
    layout="wide"
)

# -----------------------------
# HISTORY FILE
# -----------------------------
HISTORY_FILE = os.path.join(BASE_DIR, "aqi_history.json")

# -----------------------------
# HISTORY FUNCTIONS
# -----------------------------
def load_history():
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f)

def add_history(value):
    history = load_history()

    history.append({
        "time": datetime.now().strftime("%H:%M"),
        "aqi": round(value, 2)
    })

    history = history[-24:]
    save_history(history)
    return history

# -----------------------------
# AQI CLASSIFICATION
# -----------------------------
def classify_aqi(aqi):
    if aqi <= 50:
        return "Good", "green"
    elif aqi <= 100:
        return "Moderate", "orange"
    elif aqi <= 150:
        return "Unhealthy", "red"
    else:
        return "Hazardous", "darkred"

# -----------------------------
# HEADER
# -----------------------------
st.title("🌍 AQI Intelligence System")
st.caption("Real-time AI-powered air quality monitoring")

# -----------------------------
# INPUT
# -----------------------------
city = st.text_input("Enter City", "Lagos")

# -----------------------------
# LIVE DATA
# -----------------------------
data = get_live_data(city)

if "error" in data:
    st.error(data["error"])

else:

    # -----------------------------
    # PREDICTION
    # -----------------------------
    aqi_value = predict_aqi(data)

    label, color = classify_aqi(aqi_value)

    history = add_history(aqi_value)

    # -----------------------------
    # ALERTS
    # -----------------------------
    if label == "Hazardous":
        st.error("🔴 Hazardous Air Quality!")
    elif label == "Unhealthy":
        st.warning("🟠 Unhealthy Air Quality!")
    elif label == "Moderate":
        st.info("🟡 Moderate Air Quality")
    else:
        st.success("🟢 Good Air Quality")

    # -----------------------------
    # CITY INFO
    # -----------------------------
    st.subheader(f"📍 {data['city']}")

    # -----------------------------
    # METRICS
    # -----------------------------
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Temperature", f"{data['temp']} °C")
    c2.metric("Humidity", f"{data['humidity']} %")
    c3.metric("Wind", f"{data['wind']} m/s")
    c4.metric("AQI", f"{aqi_value:.1f} ({label})")

    # -----------------------------
    # POLLUTION DATA
    # -----------------------------
    st.markdown("### 🌫 Pollution Data")

    p1, p2, p3 = st.columns(3)

    p1.metric("PM2.5", data["pm2_5"])
    p2.metric("PM10", data["pm10"])
    p3.metric("NO2", data["no2"])

    p4, p5, p6 = st.columns(3)

    p4.metric("CO", data["co"])
    p5.metric("O3", data["o3"])
    p6.metric("SO2", data["so2"])

    # -----------------------------
    # WEATHER
    # -----------------------------
    st.markdown("### 🌤 Weather Condition")
    st.write(data["weather"])

    # -----------------------------
    # AQI TREND (PLOTLY)
    # -----------------------------
    st.markdown("### 📈 AQI Trend (Interactive)")

    df = pd.DataFrame(history)

    if len(df) > 1:

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df["time"],
            y=df["aqi"],
            mode="lines+markers",
            name="AQI",
            line=dict(width=3)
        ))

        fig.update_layout(
            title="AQI Trend (Last 24 Readings)",
            xaxis_title="Time",
            yaxis_title="AQI",
            template="plotly_dark"
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("Collecting AQI data...")

    # -----------------------------
    # MULTI-CITY VIEW
    # -----------------------------
    st.markdown("## 🗺 Multi-City Comparison")

    cities = ["Lagos", "Ibadan", "Abuja", "London"]

    cols = st.columns(len(cities))

    for i, c in enumerate(cities):

        d = get_live_data(c)

        with cols[i]:

            if "error" not in d:

                v = predict_aqi(d)
                l, _ = classify_aqi(v)

                st.metric(
                    label=c,
                    value=f"{v:.1f} AQI",
                    delta=l
                )