from pydantic import BaseModel


class Settings(BaseModel):
    service_name: str = "document-parsing"
    database_url: str = "data/document_parsing.db"

