import os

from pydantic import BaseModel


class Settings(BaseModel):
    service_name: str = "causal-inference"
    graph_database_url: str = os.getenv("CAUSAL_GRAPH_DATABASE_URL", ":memory:")
