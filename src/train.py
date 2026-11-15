from __future__ import annotations

import argparse
import json
import warnings

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from src.config import FEATURE_COLUMNS, MODEL_DIR, MODEL_PATH, METADATA_PATH, RESULTS_DIR
from src.data_utils import build_features, load_daily_data
from src.evaluate import regression_metrics


def candidates():
    models = {
        "Ridge": make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), Ridge(alpha=10.0)),
        "Random Forest": make_pipeline(SimpleImputer(strategy="median"), RandomForestRegressor(n_estimators=300, min_samples_leaf=2, max_features=0.8, random_state=42, n_jobs=-1)),
    }
    try:
        from xgboost import XGBRegressor

        models["XGBoost"] = make_pipeline(SimpleImputer(strategy="median"), XGBRegressor(n_estimators=400, max_depth=5, learning_rate=0.04, subsample=0.85, colsample_bytree=0.85, objective="reg:squarederror", random_state=42, n_jobs=-1))
    except ImportError:
        warnings.warn("XGBoost is not installed; continuing with Ridge and Random Forest.")
    return models


def train(data_path: str | None = None, test_year: int | None = None) -> dict:
    raw = load_daily_data(data_path)
    samples = build_features(raw)
    if samples.empty:
        raise ValueError("No trainable rows after feature creation. Check date coverage and AQI history.")
    year = test_year or int(samples["target_date"].dt.year.max())
    train_mask = samples["target_date"].dt.year < year
    test_mask = samples["target_date"].dt.year == year
    train_rows, test_rows = samples.loc[train_mask], samples.loc[test_mask]
    if train_rows.empty or test_rows.empty:
        raise ValueError(f"Need both pre-{year} training rows and {year} test rows; found {len(train_rows)} and {len(test_rows)}.")

    x_train, y_train = train_rows[FEATURE_COLUMNS], train_rows["target"]
    x_test, y_test = test_rows[FEATURE_COLUMNS], test_rows["target"]
    scores = [{"model": "Persistence", **regression_metrics(y_test, test_rows["aqi_today"])}]
    fitted = {}
    for name, estimator in candidates().items():
        estimator.fit(x_train, y_train)
        prediction = np.clip(estimator.predict(x_test), 0, None)
        scores.append({"model": name, **regression_metrics(y_test, prediction)})
        fitted[name] = estimator

    selected = min((score for score in scores if score["model"] != "Persistence"), key=lambda score: score["rmse"])
    best = fitted[selected["model"]]
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(best, MODEL_PATH)
    scores_frame = pd.DataFrame(scores).sort_values("rmse")
    scores_frame.to_csv(RESULTS_DIR / "within_city_metrics.csv", index=False)
    metadata = {
        "model": selected["model"],
        "features": FEATURE_COLUMNS,
        "test_year": year,
        "train_rows": int(len(train_rows)),
        "test_rows": int(len(test_rows)),
        "cities": sorted(raw["city"].dropna().astype(str).unique().tolist()),
        "date_start": raw["date"].min().date().isoformat(),
        "date_end": raw["date"].max().date().isoformat(),
        "scores": scores,
    }
    METADATA_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(scores_frame.to_string(index=False))
    print(f"\nSelected {selected['model']} by held-out RMSE. Artifacts saved under {MODEL_DIR}.")
    return metadata


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train and compare next-day AQI models with a chronological holdout.")
    parser.add_argument("--data", help="Path to a city-day CSV; defaults to the first CSV in data/raw.")
    parser.add_argument("--test-year", type=int, help="Held-out target year; defaults to the latest year in the CSV.")
    arguments = parser.parse_args()
    train(arguments.data, arguments.test_year)