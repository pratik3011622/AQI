from __future__ import annotations

import json
from datetime import date, timedelta

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from backend.schemas import ForecastRequest
from src.config import CITY_COORDINATES, FEATURE_COLUMNS, METADATA_PATH, MODEL_PATH
from src.data_utils import build_features, load_daily_data
from src.evaluate import aqi_category

app = FastAPI(title="Can Delhi Teach Surat?", version="0.1.0", description="Research API for cross-city next-day AQI forecasting.")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def _data() -> pd.DataFrame:
    try:
        return load_daily_data()
    except (FileNotFoundError, ValueError):
        return pd.DataFrame()


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


@app.get("/health")
def health():
    metadata = _metadata()
    return {"status": "ok", "data_loaded": not _data().empty, "model_loaded": MODEL_PATH.exists(), "model": metadata.get("model")}


@app.get("/cities")
def cities():
    frame = _data()
    available = sorted(frame["city"].dropna().astype(str).unique().tolist()) if not frame.empty else []
    return {"cities": available, "data_loaded": not frame.empty, "coordinates": {city: CITY_COORDINATES[city] for city in available if city in CITY_COORDINATES}}


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
        if frame.empty:
            raise HTTPException(status_code=503, detail="No city data available for automatic prediction.")
        selected = frame[frame["city"].str.casefold() == request.city.casefold()].sort_values("date")
        if selected.empty:
            raise HTTPException(status_code=404, detail=f"No observations found for {request.city}.")
        recent = selected.tail(7)
        if len(recent) < 7:
            raise HTTPException(status_code=422, detail=f"Need at least 7 AQI observations for {request.city}.")
        recent_values = recent["aqi"].astype(float).tolist()
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
    model = joblib.load(MODEL_PATH)
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
def transfer_matrix():
    frame = _data()
    if frame.empty:
        raise HTTPException(status_code=503, detail="Add a city-day CSV to data/raw to calculate transfer results.")
    samples = build_features(frame)
    years = samples["target_date"].dt.year
    test_year = int(years.max())
    train_samples = samples[years < test_year]
    test_samples = samples[years == test_year]
    if train_samples.empty or test_samples.empty:
        raise HTTPException(status_code=422, detail="Transfer evaluation needs at least two calendar years of observations.")
    from sklearn.impute import SimpleImputer
    from sklearn.metrics import mean_squared_error
    from sklearn.pipeline import make_pipeline
    from sklearn.ensemble import RandomForestRegressor

    cities = sorted(set(train_samples["city"]) & set(test_samples["city"]))
    matrix = []
    for train_city in cities:
        training = train_samples[train_samples["city"] == train_city]
        estimator = make_pipeline(SimpleImputer(strategy="median"), RandomForestRegressor(n_estimators=120, min_samples_leaf=2, random_state=42, n_jobs=-1))
        estimator.fit(training[FEATURE_COLUMNS], training["target"])
        for test_city in cities:
            testing = test_samples[test_samples["city"] == test_city]
            if testing.empty:
                continue
            prediction = estimator.predict(testing[FEATURE_COLUMNS])
            matrix.append({"train_city": train_city, "test_city": test_city, "rmse": round(float(np.sqrt(mean_squared_error(testing["target"], prediction))), 2), "n_test": int(len(testing))})
    return {"test_year": test_year, "cities": cities, "results": matrix}


@app.get("/explain/{city}")
def explain(city: str):
    if not MODEL_PATH.exists():
        raise HTTPException(status_code=503, detail="Train a model to enable feature importance.")
    model = joblib.load(MODEL_PATH)
    estimator = model.steps[-1][1] if hasattr(model, "steps") else model
    if hasattr(estimator, "feature_importances_"):
        values = estimator.feature_importances_
    elif hasattr(estimator, "coef_"):
        values = np.abs(estimator.coef_)
    else:
        raise HTTPException(status_code=422, detail="Feature importance is unavailable for the selected estimator.")
    ranking = sorted(zip(FEATURE_COLUMNS, values, strict=False), key=lambda item: float(item[1]), reverse=True)[:12]
    return {"city": city, "method": "model feature importance (global; not SHAP)", "features": [{"feature": name, "importance": round(float(value), 5)} for name, value in ranking]}