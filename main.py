import pandas as pd

# Load dataset
file_path = "data/openweather_weather_airpollution_top3cities_per_country.csv"

df = pd.read_csv(file_path)

# Show first rows
print(df.head())

# Show dataset info
print("\nDATASET INFO")
print(df.info())

# Show columns
print("\nCOLUMNS")
print(df.columns)

# Show shape
print("\nSHAPE")
print(df.shape)