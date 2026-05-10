from pydantic import BaseModel


class Settings(BaseModel):
    service_name: str = "entity-resolution"
    database_url: str = "data/entity_resolution.db"

