import os

from pydantic import BaseModel


class Settings(BaseModel):
    service_name: str = "signal-intelligence"
    feature_database_url: str = os.getenv("SIGNAL_FEATURE_DATABASE_URL", ":memory:")
