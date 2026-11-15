from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import make_pipeline

from src.config import FEATURE_COLUMNS, RESULTS_DIR
from src.data_utils import build_features, load_daily_data


def _estimator():
    return make_pipeline(SimpleImputer(strategy="median"), RandomForestRegressor(n_estimators=300, min_samples_leaf=2, max_features=0.8, random_state=42, n_jobs=-1))


def _scores(actual, predicted):
    return {
        "mae": float(mean_absolute_error(actual, predicted)),
        "rmse": float(np.sqrt(mean_squared_error(actual, predicted))),
    }


def run_transfer(data_path: str | None = None, test_year: int | None = None) -> pd.DataFrame:
    samples = build_features(load_daily_data(data_path))
    year = test_year or int(samples["target_date"].dt.year.max())
    train_rows = samples[samples["target_date"].dt.year < year]
    test_rows = samples[samples["target_date"].dt.year == year]
    rows = []
    for train_city in sorted(train_rows["city"].unique()):
        training = train_rows[train_rows["city"] == train_city]
        estimator = _estimator().fit(training[FEATURE_COLUMNS], training["target"])
        for test_city in sorted(test_rows["city"].unique()):
            testing = test_rows[test_rows["city"] == test_city]
            if testing.empty:
                continue
            predictions = estimator.predict(testing[FEATURE_COLUMNS])
            rows.append({"train_city": train_city, "test_city": test_city, "test_year": year, "n_test": len(testing), **_scores(testing["target"], predictions)})

    results = pd.DataFrame(rows)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    results.to_csv(RESULTS_DIR / "transfer_matrix.csv", index=False)
    return results


def run_few_shot(data_path: str | None = None, test_year: int | None = None, days: tuple[int, ...] = (30, 60, 90)) -> pd.DataFrame:
    samples = build_features(load_daily_data(data_path))
    year = test_year or int(samples["target_date"].dt.year.max())
    train_rows = samples[samples["target_date"].dt.year < year]
    test_rows = samples[samples["target_date"].dt.year == year]
    rows = []
    all_dates = samples["target_date"]
    for city in sorted(test_rows["city"].unique()):
        local_test = test_rows[test_rows["city"] == city].sort_values("target_date")
        global_train = train_rows[train_rows["city"] != city]
        if global_train.empty or local_test.empty:
            continue
        initial = local_test.iloc[0]["target_date"]
        local_history = samples[(samples["city"] == city) & (all_dates < initial)].sort_values("target_date")
        for adaptation_days in (0, *days):
            if adaptation_days:
                local_adaptation = local_history.tail(adaptation_days)
                training = pd.concat([global_train, local_adaptation], ignore_index=True)
            else:
                training = global_train
            estimator = _estimator().fit(training[FEATURE_COLUMNS], training["target"])
            predictions = estimator.predict(local_test[FEATURE_COLUMNS])
            rows.append({"city": city, "local_days": adaptation_days, "test_year": year, "n_test": len(local_test), **_scores(local_test["target"], predictions)})

    results = pd.DataFrame(rows)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    results.to_csv(RESULTS_DIR / "few_shot.csv", index=False)
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run transfer matrix and few-shot adaptation experiments.")
    parser.add_argument("--data", help="Path to a city-day CSV; defaults to a CSV in data/raw.")
    parser.add_argument("--test-year", type=int, help="Held-out target year; defaults to the latest year.")
    parser.add_argument("--experiment", choices=("transfer", "few-shot", "all"), default="all")
    args = parser.parse_args()
    if args.experiment in ("transfer", "all"):
        print("\nCross-city transfer matrix")
        print(run_transfer(args.data, args.test_year).to_string(index=False))
    if args.experiment in ("few-shot", "all"):
        print("\nFew-shot adaptation")
        print(run_few_shot(args.data, args.test_year).to_string(index=False))