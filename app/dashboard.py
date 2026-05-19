import os
import sys
import json
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

# ---------------- AUTO REFRESH ----------------
st_autorefresh = st.empty()

# ---------------- TITLE ----------------
st.title("🌍 AQI Intelligence System")
st.caption("Real-time Air Quality Monitoring + Machine Learning Intelligence")

# ---------------- CITY INPUT ----------------
city = st.text_input("Enter City", "Lagos")

# ---------------- HISTORY FILE ----------------
HISTORY_FILE = os.path.join(BASE_DIR, "aqi_history.json")

# ---------------- LOAD HISTORY ----------------
def load_history():
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except:
        return []

# ---------------- SAVE HISTORY ----------------
def save_history(data):
    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f)

# ---------------- UPDATE HISTORY ----------------
def update_history(value):

    data = load_history()

    data.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "aqi": float(value)
    })

    data = data[-50:]

    save_history(data)

    return data

# ---------------- AQI LABELS ----------------
risk_labels = {
    0: ("Good", "🟢"),
    1: ("Moderate", "🟡"),
    2: ("Sensitive Groups", "🟠"),
    3: ("Unhealthy", "🔴"),
    4: ("Hazardous", "⚫")
}

# ---------------- CITY COORDS ----------------
CITIES = {
    "Lagos": [6.5244, 3.3792],
    "Abuja": [9.0765, 7.3986],
    "Ibadan": [7.3775, 3.9470],
    "London": [51.5072, -0.1276],
    "New York": [40.7128, -74.0060]
}

# ---------------- ESTIMATE AQI ----------------
def estimate_aqi(pm25):

    if pm25 <= 12:
        return 40

    elif pm25 <= 35.4:
        return 80

    elif pm25 <= 55.4:
        return 130

    elif pm25 <= 150.4:
        return 180

    else:
        return 300

# ---------------- GET DATA ----------------
data = get_live_data(city)

# ---------------- ERROR HANDLING ----------------
if "error" in data:

    st.error(data["error"])

    st.stop()

# ---------------- MODEL PREDICTION ----------------
result = predict_aqi(data)

prediction = result["prediction"]

probabilities = result["probabilities"]

status, icon = risk_labels[prediction]

estimated_aqi = estimate_aqi(data["pm2_5"])

# ---------------- ALERTS ----------------
if prediction >= 4:
    st.error(f"{icon} Hazardous Air Quality")

elif prediction == 3:
    st.warning(f"{icon} Unhealthy Air Quality")

elif prediction == 2:
    st.warning(f"{icon} Sensitive Groups At Risk")

elif prediction == 1:
    st.info(f"{icon} Moderate Air Quality")

else:
    st.success(f"{icon} Good Air Quality")

# ---------------- METRICS ----------------
c1, c2, c3, c4 = st.columns(4)

c1.metric("🌍 City", city)
c2.metric("🌡 Temperature", f"{data['temp']} °C")
c3.metric("💧 Humidity", f"{data['humidity']} %")
c4.metric("🌫 Estimated AQI", estimated_aqi)

# ---------------- POLLUTANTS ----------------
st.markdown("## 🌫 Pollutant Monitoring")

p1, p2, p3, p4 = st.columns(4)

p1.metric("PM2.5", data["pm2_5"])
p2.metric("PM10", data["pm10"])
p3.metric("NO2", data["no2"])
p4.metric("O3", data["o3"])

p5, p6, p7, p8 = st.columns(4)

p5.metric("SO2", data["so2"])
p6.metric("CO", data["co"])
p7.metric("Pressure", data["pressure"])
p8.metric("Wind Speed", data["wind_speed"])

# ---------------- PREDICTION ----------------
st.markdown("## 🤖 ML Prediction")

st.markdown(f"# {icon} {status}")

# ---------------- CONFIDENCE ----------------
st.markdown("## 📊 Prediction Confidence")

prob_df = pd.DataFrame({
    "Risk": [
        "Good",
        "Moderate",
        "Sensitive",
        "Unhealthy",
        "Hazardous"
    ],
    "Probability": probabilities
})

st.bar_chart(
    prob_df.set_index("Risk")
)

# ---------------- HISTORY ----------------
history = update_history(estimated_aqi)

df = pd.DataFrame(history)

# ---------------- TREND ----------------
st.markdown("## 📈 AQI Trend")

if len(df) > 1:

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["time"],
        y=df["aqi"],
        mode="lines+markers"
    ))

    fig.update_layout(
        template="plotly_dark"
    )

    st.plotly_chart(fig, use_container_width=True)

# ---------------- HEATMAP ----------------
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

df_map = pd.DataFrame(
    heat_data,
    columns=["lat", "lon", "value"]
)

if not df_map.empty:

    layer = pdk.Layer(
        "HeatmapLayer",
        data=df_map,
        get_position=["lon", "lat"],
        get_weight="value",
        radiusPixels=80
    )

    view_state = pdk.ViewState(
        latitude=10,
        longitude=5,
        zoom=1.5
    )

    st.pydeck_chart(
        pdk.Deck(
            layers=[layer],
            initial_view_state=view_state
        )
    )

# ---------------- RAW DATA ----------------
with st.expander("🔍 Raw Live Data"):

    st.json(data)