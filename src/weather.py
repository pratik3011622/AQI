from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import requests

from src.config import CITY_COORDINATES, RAW_DATA_DIR

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
WEATHER_FIELDS = "temperature_2m_mean,relative_humidity_2m_mean,wind_speed_10m_mean,precipitation_sum,surface_pressure_mean"


def download_weather(city: str, start_date: str, end_date: str, output_dir: Path = RAW_DATA_DIR) -> Path:
    if city not in CITY_COORDINATES:
        raise ValueError(f"No coordinates configured for {city}. Add coordinates in src/config.py first.")
    latitude, longitude = CITY_COORDINATES[city]
    response = requests.get(
        ARCHIVE_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date,
            "end_date": end_date,
            "daily": WEATHER_FIELDS,
            "timezone": "auto",
        },
        timeout=45,
    )
    response.raise_for_status()
    daily = response.json().get("daily", {})
    result = pd.DataFrame(daily).rename(columns={"time": "date"})
    result.insert(0, "city", city)
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / f"weather_{city.lower()}_{start_date}_{end_date}.csv"
    result.to_csv(destination, index=False)
    return destination


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download daily historical weather from the Open-Meteo Archive API.")
    parser.add_argument("city", choices=sorted(CITY_COORDINATES))
    parser.add_argument("start_date", help="YYYY-MM-DD")
    parser.add_argument("end_date", help="YYYY-MM-DD")
    args = parser.parse_args()
    print(download_weather(args.city, args.start_date, args.end_date))