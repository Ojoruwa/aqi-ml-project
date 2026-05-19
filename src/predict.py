import joblib
import pandas as pd

# -----------------------------
# LOAD MODEL
# -----------------------------
MODEL_PATH = "models/aqi_model.pkl"

package = joblib.load(MODEL_PATH)

model = package["model"]
scaler = package["scaler"]
features = package["features"]

# -----------------------------
# PREDICTION FUNCTION
# -----------------------------
def predict_aqi(data_dict):

    input_df = pd.DataFrame([data_dict])

    input_df = input_df[features]

    scaled_input = scaler.transform(input_df)

    prediction = model.predict(scaled_input)[0]

    probabilities = model.predict_proba(scaled_input)[0]

    return {
        "prediction": int(prediction),
        "probabilities": probabilities.tolist()
    }