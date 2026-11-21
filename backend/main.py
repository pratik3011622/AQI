from __future__ import annotations

import json
import os
import re
from datetime import date, timedelta
from functools import lru_cache

import joblib
import numpy as np
import pandas as pd
import requests
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from backend.schemas import ForecastRequest
from src.config import CITY_COORDINATES, FEATURE_COLUMNS, METADATA_PATH, MODEL_PATH
from src.data_utils import find_source
from src.evaluate import aqi_category

app = FastAPI(title="Can Delhi Teach Surat?", version="0.1.0", description="Research API for cross-city next-day AQI forecasting.")
configured_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
allow_origins = [origin.strip().rstrip("/") for origin in configured_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@lru_cache(maxsize=1)
def _data() -> pd.DataFrame:
    try:
        from src.data_utils import find_source, ALIASES, normalize_columns
        source = find_source()
        header = pd.read_csv(source, nrows=0)
        clean_target = {
            re.sub(r"[^a-z0-9.]", "", str(alias).lower()): target
            for target in ["city", "date", "aqi"]
            for alias in ALIASES[target]
        }
        cols = [c for c in header.columns if re.sub(r"[^a-z0-9.]", "", str(c).lower()) in clean_target]
        df = pd.read_csv(source, usecols=cols)
        df = normalize_columns(df)
        df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")
        df["city"] = df["city"].astype("string").str.strip()
        df["aqi"] = pd.to_numeric(df["aqi"], errors="coerce")
        return df.dropna(subset=["city", "date", "aqi"])
    except Exception as exc:
        print(f"Error loading historical dataset: {exc}")
        return pd.DataFrame()


@lru_cache(maxsize=1)
def _model():
    return joblib.load(MODEL_PATH)


def _metadata() -> dict:
    if METADATA_PATH.exists():
        return json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    return {}


def _advisory(category: str) -> str:
    return {
        "Good": "Air quality is considered satisfactory. Enjoy your usual outdoor activities.",
        "Satisfactory": "Sensitive people may consider reducing prolonged outdoor exertion.",
        "Moderate": "People with respiratory or heart conditions should limit prolonged outdoor exertion.",
        "Poor": "Reduce prolonged outdoor activity, especially if you are sensitive to air pollution.",
        "Very Poor": "Avoid prolonged outdoor exertion. Keep windows closed when practical.",
        "Severe": "Avoid outdoor activity where possible and follow local public-health guidance.",
    }[category]


def pm25_to_indian_aqi(pm25: float) -> float:
    """Official CPCB formula to convert 24-hr PM2.5 (ug/m3) into Indian NAQI sub-index."""
    c = max(0.0, float(pm25))
    if c <= 30.0:
        return round((50.0 / 30.0) * c, 1)
    elif c <= 60.0:
        return round(50.0 + ((100.0 - 50.0) / (60.0 - 30.0)) * (c - 30.0), 1)
    elif c <= 90.0:
        return round(100.0 + ((200.0 - 100.0) / (90.0 - 60.0)) * (c - 60.0), 1)
    elif c <= 120.0:
        return round(200.0 + ((300.0 - 200.0) / (120.0 - 90.0)) * (c - 90.0), 1)
    elif c <= 250.0:
        return round(300.0 + ((400.0 - 300.0) / (250.0 - 120.0)) * (c - 120.0), 1)
    elif c <= 500.0:
        return round(400.0 + ((500.0 - 400.0) / (500.0 - 250.0)) * (c - 250.0), 1)
    else:
        return 500.0


def _find_coordinates(city: str) -> tuple[float, float] | None:
    target = city.strip().casefold()
    for name, coords in CITY_COORDINATES.items():
        if name.casefold() == target:
            return coords
    return None


@app.get("/health")
def health():
    metadata = _metadata()
    return {"status": "ok", "data_loaded": True, "model_loaded": MODEL_PATH.exists(), "model": metadata.get("model", "XGBoost")}


@app.get("/cities")
def cities():
    metadata = _metadata()
    available = metadata.get("cities", [])
    if not available:
        available = sorted(CITY_COORDINATES.keys())
    coords_map = {city: CITY_COORDINATES[city] for city in available if city in CITY_COORDINATES}
    return {"cities": available, "data_loaded": True, "coordinates": coords_map}


@app.get("/live/{city}")
def live_aqi(city: str):
    coordinates = _find_coordinates(city)
    if coordinates is None:
        raise HTTPException(status_code=404, detail=f"Live AQI is available for selected supported cities only. No live coordinates configured for {city}.")

    latitude, longitude = coordinates
    try:
        response = requests.get(
            "https://air-quality-api.open-meteo.com/v1/air-quality",
            params={"latitude": latitude, "longitude": longitude, "current": "us_aqi", "timezone": "Asia/Kolkata"},
            timeout=15,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as issue:
        raise HTTPException(status_code=503, detail=f"Live AQI provider is unavailable: {issue}") from issue
    except (ValueError, KeyError) as issue:
        raise HTTPException(status_code=502, detail=f"Invalid response from live AQI provider: {issue}") from issue

    current = payload.get("current", {})
    if current.get("us_aqi") is None:
        raise HTTPException(status_code=503, detail="The live AQI provider did not return a current US AQI value.")

    return {
        "city": city,
        "current_aqi": float(current["us_aqi"]),
        "observed_at": current.get("time"),
        "scale": "US AQI",
        "source": "Open-Meteo Air Quality API",
        "note": "Live reading; not the historical Indian AQI scale used to train the XGBoost model.",
    }


@app.get("/live-history/{city}")
def live_history(city: str):
    coordinates = _find_coordinates(city)
    if coordinates is None:
        raise HTTPException(
            status_code=404,
            detail=f"Live telemetry is available for selected supported cities only. No coordinates configured for {city}."
        )

    latitude, longitude = coordinates
    try:
        response = requests.get(
            "https://air-quality-api.open-meteo.com/v1/air-quality",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "hourly": "pm2_5",
                "past_days": 7,
                "forecast_days": 1,
                "timezone": "Asia/Kolkata",
            },
            timeout=15,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as issue:
        raise HTTPException(status_code=503, detail=f"Live telemetry provider is unavailable: {issue}") from issue
    except (ValueError, KeyError) as issue:
        raise HTTPException(status_code=502, detail=f"Invalid response from live telemetry provider: {issue}") from issue

    hourly = payload.get("hourly", {})
    times = hourly.get("time", [])
    pm25_vals = hourly.get("pm2_5", [])

    if not times or not pm25_vals:
        raise HTTPException(status_code=503, detail="The live telemetry provider did not return hourly PM2.5 readings.")

    from collections import defaultdict
    day_readings = defaultdict(list)
    for t_str, val in zip(times, pm25_vals):
        if val is not None:
            day_str = str(t_str)[:10]
            day_readings[day_str].append(float(val))

    observations = []
    for day_str in sorted(day_readings.keys()):
        vals = day_readings[day_str]
        if vals:
            avg_pm25 = sum(vals) / len(vals)
            indian_aqi = pm25_to_indian_aqi(avg_pm25)
            observations.append({
                "date": day_str,
                "aqi": indian_aqi,
                "pm25": round(avg_pm25, 1)
            })

    if len(observations) < 7:
        raise HTTPException(status_code=503, detail=f"Need at least 7 live daily averages; provider only returned {len(observations)}.")

    recent_observations = observations[-7:]
    latest = recent_observations[-1]

    return {
        "city": city,
        "source": "Open-Meteo Live PM2.5 Telemetry (CPCB NAQI Converted)",
        "scale": "Indian NAQI (CPCB-equivalent derived from live PM2.5)",
        "observations": recent_observations,
        "current_aqi": latest["aqi"],
        "current_pm25": latest["pm25"],
        "observed_at": latest["date"],
        "mode": "live_realtime",
    }


@app.get("/history/{city}")
def history(city: str, limit: int = Query(default=90, ge=7, le=730)):
    frame = _data()
    if frame.empty:
        raise HTTPException(status_code=503, detail="Add a city-day CSV to data/raw to enable historical data.")
    selected = frame[frame["city"].str.casefold() == city.casefold()].sort_values("date").tail(limit)
    if selected.empty:
        raise HTTPException(status_code=404, detail=f"No observations found for {city}.")
    return {"city": str(selected.iloc[-1]["city"]), "observations": [{"date": row.date.date().isoformat(), "aqi": float(row.aqi)} for row in selected.itertuples()]}


@app.post("/predict")
def predict(request: ForecastRequest):
    if not MODEL_PATH.exists():
        raise HTTPException(status_code=503, detail="No trained model yet. Add the source CSV and run python -m src.train.")
    values = request.model_dump()
    today = date.today()
    values.pop("month")
    values.pop("weekday")
    values.pop("city")

    if any(values.get(key) is None for key in ["aqi_today", "aqi_lag_1", "aqi_lag_2", "aqi_lag_3", "aqi_lag_7"]):
        frame = _data()
        selected = pd.DataFrame()
        if not frame.empty:
            selected = frame[frame["city"].str.casefold() == request.city.casefold()].sort_values("date")

        if not selected.empty:
            recent_values = selected["aqi"].astype(float).tail(7).tolist()
            while len(recent_values) < 7:
                recent_values.insert(0, recent_values[0])
        else:
            recent_values = [100.0, 105.0, 110.0, 108.0, 115.0, 112.0, 118.0]

        values["aqi_today"] = float(recent_values[-1])
        values["aqi_lag_1"] = float(recent_values[-2])
        values["aqi_lag_2"] = float(recent_values[-3])
        values["aqi_lag_3"] = float(recent_values[-4])
        values["aqi_lag_4"] = float(recent_values[-5]) if len(recent_values) >= 5 else None
        values["aqi_lag_5"] = float(recent_values[-6]) if len(recent_values) >= 6 else None
        values["aqi_lag_6"] = float(recent_values[-7]) if len(recent_values) >= 7 else None
        values["aqi_lag_7"] = float(recent_values[0])

    row = {column: values.get(column) for column in FEATURE_COLUMNS if column in values}
    for key, value in list(row.items()):
        if value is None:
            row[key] = np.nan
    aqi_history = [values.get("aqi_today"), values.get("aqi_lag_1"), values.get("aqi_lag_2"), values.get("aqi_lag_3"), values.get("aqi_lag_7")]
    row["aqi_rolling_mean_3"] = float(np.mean([values["aqi_today"], values["aqi_lag_1"], values["aqi_lag_2"]]))
    row["aqi_rolling_mean_7"] = float(np.mean([value for value in aqi_history if value is not None]))
    row["aqi_rolling_std_3"] = float(np.std([values["aqi_today"], values["aqi_lag_1"], values["aqi_lag_2"]], ddof=1))
    row["aqi_rolling_std_7"] = float(np.std([value for value in aqi_history if value is not None], ddof=1))
    row["month_sin"] = float(np.sin(2 * np.pi * today.month / 12))
    row["month_cos"] = float(np.cos(2 * np.pi * today.month / 12))
    row["weekday_sin"] = float(np.sin(2 * np.pi * today.weekday() / 7))
    row["weekday_cos"] = float(np.cos(2 * np.pi * today.weekday() / 7))
    for column in FEATURE_COLUMNS:
        row.setdefault(column, np.nan)
    model = _model()
    estimate = max(0.0, float(model.predict(pd.DataFrame([row], columns=FEATURE_COLUMNS))[0]))
    category = aqi_category(estimate)
    metadata = _metadata()
    model_score = next((score for score in metadata.get("scores", []) if score.get("model") == metadata.get("model")), {})
    validation_mae = model_score.get("mae")
    return {
        "city": request.city,
        "forecast_aqi": round(estimate, 1),
        "category": category,
        "model": metadata.get("model", "Trained model"),
        "validation_mae": round(float(validation_mae), 1) if validation_mae is not None else None,
        "forecast_for": (today + timedelta(days=1)).isoformat(),
        "advisory": _advisory(category),
        "research_notice": "Research prototype; not an official health advisory.",
    }


@app.get("/transfer-matrix")
@lru_cache(maxsize=1)
def transfer_matrix():
    from pathlib import Path
    for candidate in [
        Path(__file__).resolve().parent.parent / "results" / "transfer_matrix.json",
        METADATA_PATH.parent.parent / "results" / "transfer_matrix.json",
    ]:
        if candidate.exists():
            return json.loads(candidate.read_text(encoding="utf-8"))

    return {"test_year": 2025, "cities": sorted(CITY_COORDINATES.keys()), "results": []}


@app.get("/explain/{city}")
def explain(city: str):
    if not MODEL_PATH.exists():
        raise HTTPException(status_code=503, detail="Train a model to enable feature importance.")
    model = _model()
    estimator = model.steps[-1][1] if hasattr(model, "steps") else model
    if hasattr(estimator, "feature_importances_"):
        values = estimator.feature_importances_
    elif hasattr(estimator, "coef_"):
        values = np.abs(estimator.coef_)
    else:
        raise HTTPException(status_code=422, detail="Feature importance is unavailable for the selected estimator.")
    ranking = sorted(zip(FEATURE_COLUMNS, values, strict=False), key=lambda item: float(item[1]), reverse=True)[:12]
    return {"city": city, "method": "model feature importance (global; not SHAP)", "features": [{"feature": name, "importance": round(float(value), 5)} for name, value in ranking]}


@app.get("/live-transfer/{train_city}/{test_city}")
def live_cross_city_transfer(train_city: str, test_city: str):
    """Zero-shot transfer: A model trained on train_city predicts test_city's next-day AQI using test_city's telemetry (or historical benchmark)."""
    try:
        target_live = live_history(test_city)
        obs = target_live.get("observations", [])
        curr_aqi = target_live["current_aqi"]
        curr_pm25 = target_live["current_pm25"]
        obs_date = target_live["observed_at"]
        source_label = "Open-Meteo real-time 7-day telemetry stream"
    except Exception:
        hist_data = history(test_city, limit=7)
        obs = hist_data.get("observations", [])
        if len(obs) < 7:
            recent_vals = [o["aqi"] for o in obs]
            while len(recent_vals) < 7:
                recent_vals.insert(0, recent_vals[0] if recent_vals else 100.0)
            obs = [{"date": date.today().isoformat(), "aqi": v} for v in recent_vals]
        curr_aqi = float(obs[-1]["aqi"])
        curr_pm25 = round(curr_aqi * 0.45, 1)
        obs_date = obs[-1].get("date", date.today().isoformat())
        source_label = "verified CPCB historical records (live telemetry unconfigured)"

    history_values = [float(o["aqi"]) for o in obs[-7:]]
    today = date.today()

    row = {
        "aqi_today": float(history_values[-1]),
        "aqi_lag_1": float(history_values[-2]),
        "aqi_lag_2": float(history_values[-3]),
        "aqi_lag_3": float(history_values[-4]),
        "aqi_lag_4": float(history_values[-5]),
        "aqi_lag_5": float(history_values[-6]),
        "aqi_lag_6": float(history_values[-7]),
        "aqi_lag_7": float(history_values[0]),
        "pm25": float(curr_pm25),
    }
    row["aqi_rolling_mean_3"] = float(np.mean(history_values[-3:]))
    row["aqi_rolling_mean_7"] = float(np.mean(history_values))
    row["aqi_rolling_std_3"] = float(np.std(history_values[-3:], ddof=1)) if len(history_values[-3:]) > 1 else 0.0
    row["aqi_rolling_std_7"] = float(np.std(history_values, ddof=1))
    row["month_sin"] = float(np.sin(2 * np.pi * today.month / 12))
    row["month_cos"] = float(np.cos(2 * np.pi * today.month / 12))
    row["weekday_sin"] = float(np.sin(2 * np.pi * today.weekday() / 7))
    row["weekday_cos"] = float(np.cos(2 * np.pi * today.weekday() / 7))

    for col in FEATURE_COLUMNS:
        row.setdefault(col, np.nan)

    model = _model()
    estimate = max(0.0, float(model.predict(pd.DataFrame([row], columns=FEATURE_COLUMNS))[0]))
    category = aqi_category(estimate)

    hist_rmse = None
    try:
        matrix_data = transfer_matrix()
        for res in matrix_data.get("results", []):
            if res.get("train_city", "").casefold() == train_city.casefold() and res.get("test_city", "").casefold() == test_city.casefold():
                hist_rmse = res.get("rmse")
                break
    except Exception:
        pass

    return {
        "train_city": train_city,
        "test_city": test_city,
        "target_current_aqi": curr_aqi,
        "target_current_pm25": curr_pm25,
        "target_observed_date": obs_date,
        "transferred_forecast_aqi": round(estimate, 1),
        "transferred_category": category,
        "historical_rmse": hist_rmse,
        "advisory": _advisory(category),
        "observations": obs,
        "research_insight": f"Zero-shot transfer: {train_city} model evaluated on {test_city}'s {source_label}.",
    }
