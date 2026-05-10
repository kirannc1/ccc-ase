from pydantic import BaseModel


class Settings(BaseModel):
    service_name: str = "source-connector"
    database_url: str = "data/source_connector.db"

