from __future__ import annotations

import numpy as np
from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error, mean_squared_error, r2_score


def aqi_category(value: float) -> str:
    if value <= 50:
        return "Good"
    if value <= 100:
        return "Satisfactory"
    if value <= 200:
        return "Moderate"
    if value <= 300:
        return "Poor"
    if value <= 400:
        return "Very Poor"
    return "Severe"


def regression_metrics(actual, predicted) -> dict[str, float]:
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    labels = ["Good", "Satisfactory", "Moderate", "Poor", "Very Poor", "Severe"]
    actual_bands = [aqi_category(value) for value in actual]
    predicted_bands = [aqi_category(value) for value in predicted]
    return {
        "mae": float(mean_absolute_error(actual, predicted)),
        "rmse": float(np.sqrt(mean_squared_error(actual, predicted))),
        "r2": float(r2_score(actual, predicted)) if len(actual) > 1 else float("nan"),
        "category_accuracy": float(accuracy_score(actual_bands, predicted_bands)),
        "macro_f1": float(f1_score(actual_bands, predicted_bands, labels=labels, average="macro", zero_division=0)),
    }