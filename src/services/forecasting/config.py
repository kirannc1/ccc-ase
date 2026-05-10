import os

from pydantic import BaseModel


class Settings(BaseModel):
    service_name: str = "forecasting"
    feature_database_url: str = os.getenv("FORECAST_FEATURE_DATABASE_URL", ":memory:")
