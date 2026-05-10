import os

from pydantic import BaseModel


class Settings(BaseModel):
    service_name: str = "policy-service"
    feature_database_url: str = os.getenv("POLICY_FEATURE_DATABASE_URL", ":memory:")
