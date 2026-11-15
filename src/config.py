from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = ROOT / "data" / "raw"
PROCESSED_DATA_DIR = ROOT / "data" / "processed"
MODEL_DIR = ROOT / "models"
RESULTS_DIR = ROOT / "results"

DATE_COLUMN = "date"
CITY_COLUMN = "city"
TARGET_COLUMN = "aqi"

POLLUTANTS = ["pm25", "pm10", "no2", "so2", "co", "o3"]
WEATHER = ["temperature_2m_mean", "relative_humidity_2m_mean", "wind_speed_10m_mean", "precipitation_sum", "surface_pressure_mean"]
AQI_LAGS = [1, 2, 3, 7]
PM25_LAGS = [1, 2, 3, 7]

FEATURE_COLUMNS = (
    ["aqi_today"]
    + [f"aqi_lag_{lag}" for lag in AQI_LAGS]
    + ["pm25_today"]
    + [f"pm25_lag_{lag}" for lag in PM25_LAGS]
    + [f"aqi_rolling_mean_{window}" for window in (3, 7)]
    + [f"aqi_rolling_std_{window}" for window in (3, 7)]
    + POLLUTANTS
    + WEATHER
    + ["month_sin", "month_cos", "weekday_sin", "weekday_cos"]
)

CITY_COORDINATES = {
    "Ahmedabad": (23.0225, 72.5714),
    "Bengaluru": (12.9716, 77.5946),
    "Chennai": (13.0827, 80.2707),
    "Delhi": (28.6139, 77.2090),
    "Hyderabad": (17.3850, 78.4867),
    "Kolkata": (22.5726, 88.3639),
    "Mumbai": (19.0760, 72.8777),
    "Pune": (18.5204, 73.8567),
}

MODEL_PATH = MODEL_DIR / "best_model.joblib"
METADATA_PATH = MODEL_DIR / "metadata.json"