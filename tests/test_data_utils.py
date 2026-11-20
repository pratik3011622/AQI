import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from src.config import FEATURE_COLUMNS
from src.data_utils import build_features, load_daily_data, normalize_columns
from src.evaluate import aqi_category


class FeatureIntegrityTests(unittest.TestCase):
    def test_calendar_gap_is_interpolated_within_city(self):
        dates = pd.date_range("2024-01-01", periods=12).delete(5)
        values = [10, 20, 30, 40, 50, 70, 80, 90, 100, 110, 120]
        frame = pd.DataFrame([{"City": "A", "Date": day, "AQI": value} for day, value in zip(dates, values, strict=True)])
        samples = build_features(normalize_columns(frame))
        jan_nine = samples.loc[samples["date"].eq(pd.Timestamp("2024-01-09"))].iloc[0]
        self.assertEqual(jan_nine["aqi_lag_1"], 80)
        self.assertEqual(jan_nine["aqi_rolling_mean_3"], 80)
        self.assertEqual(jan_nine["target"], 100)

    def test_city_is_not_a_model_feature(self):
        self.assertNotIn("city", FEATURE_COLUMNS)

    def test_long_aqi_gap_is_not_interpolated(self):
        dates = pd.date_range("2024-01-01", periods=18).delete([5, 6, 7, 8])
        values = [10 * (index + 1) for index in range(len(dates))]
        samples = build_features(pd.DataFrame([{"city": "A", "date": day, "aqi": value} for day, value in zip(dates, values, strict=True)]))
        self.assertNotIn(pd.Timestamp("2024-01-08"), samples["date"].tolist())
        self.assertIn(pd.Timestamp("2024-01-17"), samples["date"].tolist())

    def test_weather_file_joins_by_city_and_date(self):
        with tempfile.TemporaryDirectory() as directory:
            raw_dir = Path(directory)
            pd.DataFrame([{"City": "A", "Date": "2024-01-01", "AQI": 80}]).to_csv(raw_dir / "city_day.csv", index=False)
            pd.DataFrame([{"city": "A", "date": "2024-01-01", "temperature_2m_mean": 22.5}]).to_csv(raw_dir / "weather_a.csv", index=False)
            with patch("src.config.RAW_DATA_DIR", raw_dir):
                result = load_daily_data()
        self.assertEqual(result.loc[0, "temperature_2m_mean"], 22.5)

    def test_real_aqi_csv_schema_is_normalized(self):
        frame = pd.DataFrame([
            {"date": "30-04-2025", "state": "Maharashtra", "area": "Amravati", "number_of_monitoring_stations": 2, "prominent_pollutants": "PM10", "aqi_value": 78, "air_quality_status": "Satisfactory", "unit": "µg/m³", "note": ""},
            {"date": "01-05-2025", "state": "Maharashtra", "area": "Amravati", "number_of_monitoring_stations": 2, "prominent_pollutants": "PM10", "aqi_value": 82, "air_quality_status": "Moderate", "unit": "µg/m³", "note": ""},
        ])
        normalized = normalize_columns(frame)
        self.assertEqual(list(normalized.columns), ["date", "state", "city", "number_of_monitoring_stations", "prominent_pollutants", "aqi", "air_quality_status", "unit", "note"])
        self.assertEqual(normalized.loc[0, "city"], "Amravati")
        self.assertEqual(normalized.loc[0, "aqi"], 78)

    def test_category_boundaries(self):
        self.assertEqual(aqi_category(50), "Good")
        self.assertEqual(aqi_category(51), "Satisfactory")
        self.assertEqual(aqi_category(100), "Satisfactory")
        self.assertEqual(aqi_category(101), "Moderate")
        self.assertEqual(aqi_category(401), "Severe")

    def test_city_coordinates_case_insensitive_lookup(self):
        from backend.main import _find_coordinates
        self.assertIsNotNone(_find_coordinates("Delhi"))
        self.assertIsNotNone(_find_coordinates("delhi"))
        self.assertIsNotNone(_find_coordinates("DELHI "))
        self.assertIsNotNone(_find_coordinates("Jaipur"))
        self.assertIsNone(_find_coordinates("NonExistentCityXYZ"))



if __name__ == "__main__":
    unittest.main()