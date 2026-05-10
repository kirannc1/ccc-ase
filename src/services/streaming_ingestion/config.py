from pydantic import BaseModel


class Settings(BaseModel):
    service_name: str = "streaming-ingestion"
    database_url: str = "data/streaming_ingestion.db"

