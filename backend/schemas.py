from pydantic import BaseModel, Field


class ForecastRequest(BaseModel):
    city: str = Field(min_length=1, max_length=80)
    aqi_today: float | None = Field(default=None, ge=0, le=1000)
    aqi_lag_1: float | None = Field(default=None, ge=0, le=1000)
    aqi_lag_2: float | None = Field(default=None, ge=0, le=1000)
    aqi_lag_3: float | None = Field(default=None, ge=0, le=1000)
    aqi_lag_4: float | None = Field(default=None, ge=0, le=1000)
    aqi_lag_5: float | None = Field(default=None, ge=0, le=1000)
    aqi_lag_6: float | None = Field(default=None, ge=0, le=1000)
    aqi_lag_7: float | None = Field(default=None, ge=0, le=1000)
    pm25_today: float | None = Field(default=None, ge=0)
    pm25_lag_1: float | None = Field(default=None, ge=0)
    pm25_lag_2: float | None = Field(default=None, ge=0)
    pm25_lag_3: float | None = Field(default=None, ge=0)
    pm25_lag_7: float | None = Field(default=None, ge=0)
    pm25: float | None = Field(default=None, ge=0)
    pm10: float | None = Field(default=None, ge=0)
    no2: float | None = Field(default=None, ge=0)
    so2: float | None = Field(default=None, ge=0)
    co: float | None = Field(default=None, ge=0)
    o3: float | None = Field(default=None, ge=0)
    temperature_2m_mean: float | None = None
    relative_humidity_2m_mean: float | None = Field(default=None, ge=0, le=100)
    wind_speed_10m_mean: float | None = Field(default=None, ge=0)
    precipitation_sum: float | None = Field(default=None, ge=0)
    surface_pressure_mean: float | None = Field(default=None, ge=0)
    month: int = Field(default=1, ge=1, le=12)
    weekday: int = Field(default=0, ge=0, le=6)


class ForecastResponse(BaseModel):
    city: str
    forecast_aqi: float
    category: str
    model: str
    forecast_for: str
    advisory: str
    research_notice: str = "Research prototype; not an official health advisory."