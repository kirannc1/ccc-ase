from pydantic import BaseModel


class Settings(BaseModel):
    service_name: str = "knowledge-graph"
    database_url: str = "data/knowledge_graph.db"

