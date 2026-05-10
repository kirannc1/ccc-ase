from pydantic import BaseModel


class Settings(BaseModel):
    service_name: str = "batch-ingestion"
    database_url: str = "data/batch_ingestion.db"

