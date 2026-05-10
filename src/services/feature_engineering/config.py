from pydantic import BaseModel


class Settings(BaseModel):
    service_name: str = "feature-engineering"
    database_url: str = "data/feature_engineering.db"

