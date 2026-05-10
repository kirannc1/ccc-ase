import os

from pydantic import BaseModel


class Settings(BaseModel):
    service_name: str = "anomaly-detection"
    feature_database_url: str = os.getenv("ANOMALY_FEATURE_DATABASE_URL", ":memory:")
