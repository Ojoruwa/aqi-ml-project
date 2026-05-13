import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

def build_model():
    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=(10, 1)),
        LSTM(32),
        Dense(1)
    ])

    model.compile(optimizer="adam", loss="mse")
    return model

def train_lstm(data):
    data = np.array(data)

    if len(data) < 15:
        return None

    X, y = [], []

    for i in range(len(data) - 10):
        X.append(data[i:i+10])
        y.append(data[i+10])

    X = np.array(X).reshape(-1, 10, 1)
    y = np.array(y)

    model = build_model()
    model.fit(X, y, epochs=5, verbose=0)

    return model

def predict_lstm(model, data):
    data = np.array(data[-10:]).reshape(1, 10, 1)
    return float(model.predict(data)[0][0])