from pydantic import BaseModel


class Settings(BaseModel):
    service_name: str = "semantic-normalization"
    database_url: str = "data/semantic_normalization.db"

