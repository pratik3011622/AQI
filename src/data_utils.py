"""Load supported AQI CSVs and create strictly past-informed next-day features."""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

from src.config import FEATURE_COLUMNS


ALIASES = {
    "city": {"city", "cityname", "stationcity", "area", "location", "district"},
    "date": {"date", "datetime", "day"},
    "aqi": {"aqi", "airqualityindex", "index", "aqi_value", "aqivalue"},
    "pm25": {"pm25", "pm2.5", "pm2_5"},
    "pm10": {"pm10"},
    "no2": {"no2"},
    "so2": {"so2"},
    "co": {"co"},
    "o3": {"o3", "ozone"},
    "temperature_2m_mean": {"temperature_2m_mean", "temperature", "temp", "t2m"},
    "relative_humidity_2m_mean": {"relative_humidity_2m_mean", "humidity", "relativehumidity"},
    "wind_speed_10m_mean": {"wind_speed_10m_mean", "windspeed", "wind_speed"},
    "precipitation_sum": {"precipitation_sum", "precipitation", "rainfall", "rain"},
    "surface_pressure_mean": {"surface_pressure_mean", "pressure", "surfacepressure"},
}


def _key(value: object) -> str:
    return re.sub(r"[^a-z0-9.]", "", str(value).strip().lower())


def normalize_columns(frame: pd.DataFrame, require_aqi: bool = True) -> pd.DataFrame:
    lookup = {_key(alias): canonical for canonical, aliases in ALIASES.items() for alias in aliases}
    rename = {column: lookup[_key(column)] for column in frame.columns if _key(column) in lookup}
    normalized = frame.rename(columns=rename).copy()
    required = {"city", "date", "aqi"} if require_aqi else {"city", "date"}
    if not required.issubset(normalized.columns):
        raise ValueError("CSV must include city, date, and AQI columns (for example City, Date, AQI).")
    return normalized


def find_source(path: str | Path | None = None) -> Path:
    if path:
        source = Path(path).expanduser().resolve()
        if not source.is_file():
            raise FileNotFoundError(f"Dataset not found: {source}")
        return source
    from src.config import RAW_DATA_DIR

    candidates = sorted(RAW_DATA_DIR.glob("*.csv"))
    if not candidates:
        raise FileNotFoundError("No CSV found in data/raw. Add the source city-day CSV first.")
    valid = []
    for candidate in candidates:
        try:
            normalize_columns(pd.read_csv(candidate, nrows=0))
            valid.append(candidate)
        except (OSError, ValueError, pd.errors.ParserError, UnicodeDecodeError):
            continue
    if not valid:
        raise FileNotFoundError("No AQI CSV found in data/raw. The source must include city, date, and AQI columns.")
    preferred = [candidate for candidate in valid if "city_day" in candidate.name.lower()]
    return preferred[0] if preferred else valid[0]


def load_daily_data(path: str | Path | None = None) -> pd.DataFrame:
    source = find_source(path)
    frame = normalize_columns(pd.read_csv(source))
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce", dayfirst=True)
    frame["city"] = frame["city"].astype("string").str.strip()
    numeric = [column for column in frame.columns if column not in {"city", "date", "aqi_bucket", "state", "air_quality_status", "unit", "note", "prominent_pollutants"}]
    for column in numeric:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    from src.config import RAW_DATA_DIR

    weather_frames = []
    for candidate in RAW_DATA_DIR.glob("*.csv"):
        if candidate.resolve() == source.resolve():
            continue
        try:
            weather = normalize_columns(pd.read_csv(candidate), require_aqi=False)
        except (OSError, ValueError, pd.errors.ParserError, UnicodeDecodeError):
            continue
        weather_columns = [column for column in weather.columns if column in {"temperature_2m_mean", "relative_humidity_2m_mean", "wind_speed_10m_mean", "precipitation_sum", "surface_pressure_mean"}]
        if not weather_columns:
            continue
        weather["date"] = pd.to_datetime(weather["date"], errors="coerce", dayfirst=False)
        weather["city"] = weather["city"].astype("string").str.strip()
        weather_frames.append(weather[["city", "date", *weather_columns]])
    if weather_frames:
        weather = pd.concat(weather_frames, ignore_index=True).dropna(subset=["city", "date"])
        weather = weather.drop_duplicates(["city", "date"], keep="last")
        overlap = [column for column in weather.columns if column not in {"city", "date"} and column in frame.columns]
        if overlap:
            frame = frame.drop(columns=overlap)
        frame = frame.merge(weather, on=["city", "date"], how="left", validate="many_to_one")
    frame = frame.dropna(subset=["city", "date"])
    frame = frame.drop_duplicates(["city", "date"], keep="last")
    return frame.sort_values(["city", "date"]).reset_index(drop=True)


def build_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Build X(t) -> AQI(t+1); city is retained for grouping, never as a feature."""
    frame = normalize_columns(frame) if not {"city", "date", "aqi"}.issubset(frame.columns) else frame.copy()
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    frame = frame.dropna(subset=["city", "date"]).sort_values(["city", "date"]).copy()
    for column in FEATURE_COLUMNS:
        if column not in frame:
            frame[column] = np.nan

    parts = []
    for city, city_frame in frame.groupby("city", sort=False):
        city_frame = city_frame.sort_values("date").set_index("date")
        city_frame = city_frame[~city_frame.index.duplicated(keep="last")]
        daily_index = pd.date_range(city_frame.index.min(), city_frame.index.max(), freq="D")
        city_frame = city_frame.reindex(daily_index)
        city_frame.index.name = "date"
        city_frame["city"] = city
        numeric_columns = city_frame.select_dtypes(include="number").columns
        for column in numeric_columns:
            missing = city_frame[column].isna()
            gap_groups = (~missing).cumsum()
            gap_lengths = missing.groupby(gap_groups).transform("sum")
            interpolated = city_frame[column].interpolate(method="time", limit=3, limit_area="inside")
            city_frame[column] = interpolated.mask(missing & gap_lengths.gt(3), np.nan)
        city_frame = city_frame.reset_index()
        aqi = city_frame["aqi"].astype(float)
        pm25 = city_frame["pm25"].astype(float) if "pm25" in city_frame else pd.Series(np.nan, index=city_frame.index)
        city_frame["aqi_today"] = aqi
        city_frame["pm25_today"] = pm25
        for lag in (1, 2, 3, 7):
            city_frame[f"aqi_lag_{lag}"] = aqi.shift(lag)
            city_frame[f"pm25_lag_{lag}"] = pm25.shift(lag)
        for window in (3, 7):
            city_frame[f"aqi_rolling_mean_{window}"] = aqi.rolling(window, min_periods=window).mean()
            city_frame[f"aqi_rolling_std_{window}"] = aqi.rolling(window, min_periods=window).std()
        for column in ("pm25", "pm10", "no2", "so2", "co", "o3", "temperature_2m_mean", "relative_humidity_2m_mean", "wind_speed_10m_mean", "precipitation_sum", "surface_pressure_mean"):
            if column not in city_frame:
                city_frame[column] = np.nan
        city_frame["month_sin"] = np.sin(2 * np.pi * city_frame["date"].dt.month / 12)
        city_frame["month_cos"] = np.cos(2 * np.pi * city_frame["date"].dt.month / 12)
        city_frame["weekday_sin"] = np.sin(2 * np.pi * city_frame["date"].dt.dayofweek / 7)
        city_frame["weekday_cos"] = np.cos(2 * np.pi * city_frame["date"].dt.dayofweek / 7)
        city_frame["target"] = aqi.shift(-1)
        city_frame["target_date"] = city_frame["date"].shift(-1)
        parts.append(city_frame)

    result = pd.concat(parts, ignore_index=True)
    required = ["aqi_today", *[f"aqi_lag_{lag}" for lag in (1, 2, 3, 7)]]
    result = result.dropna(subset=required + ["target"])
    return result.reset_index(drop=True)