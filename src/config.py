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
    "Agra": (27.1767, 78.0081),
    "Ahmedabad": (23.0225, 72.5714),
    "Amritsar": (31.6340, 74.8723),
    "Bengaluru": (12.9716, 77.5946),
    "Bhopal": (23.2599, 77.4126),
    "Bhubaneswar": (20.2961, 85.8245),
    "Chandigarh": (30.7333, 76.7794),
    "Chennai": (13.0827, 80.2707),
    "Coimbatore": (11.0168, 76.9558),
    "Delhi": (28.6139, 77.2090),
    "Ghaziabad": (28.6692, 77.4538),
    "Greater Noida": (28.4744, 77.5040),
    "Guwahati": (26.1445, 91.7362),
    "Howrah": (22.5958, 88.2636),
    "Hyderabad": (17.3850, 78.4867),
    "Indore": (22.7196, 75.8577),
    "Jaipur": (26.9124, 75.7873),
    "Kanpur": (26.4499, 80.3319),
    "Kochi": (9.9312, 76.2673),
    "Kolkata": (22.5726, 88.3639),
    "Lucknow": (26.8467, 80.9462),
    "Meerut": (28.9845, 77.7064),
    "Moradabad": (28.8386, 78.7733),
    "Mumbai": (19.0760, 72.8777),
    "Nagpur": (21.1458, 79.0882),
    "Nashik": (19.9975, 73.7898),
    "Noida": (28.5355, 77.3910),
    "Patna": (25.5941, 85.1376),
    "Prayagraj": (25.4358, 81.8463),
    "Pune": (18.5204, 73.8567),
    "Surat": (21.1702, 72.8311),
    "Thiruvananthapuram": (8.5241, 76.9366),
    "Vadodara": (22.3072, 73.1812),
    "Varanasi": (25.3176, 82.9739),
    "Visakhapatnam": (17.6868, 83.2185),
}

MODEL_PATH = MODEL_DIR / "best_model.joblib"
METADATA_PATH = MODEL_DIR / "metadata.json"