from fastapi import FastAPI

from services.common.models import GraphRelation, GraphWriteRequest, HealthResponse
from services.common.storage import SqliteStore
from services.knowledge_graph.config import Settings
from services.knowledge_graph.core import KnowledgeGraphService

settings = Settings()
store = SqliteStore(settings.database_url)
service = KnowledgeGraphService(store)
app = FastAPI(title=settings.service_name)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(service=settings.service_name)


@app.post("/graph/upsert", response_model=GraphRelation)
def upsert(request: GraphWriteRequest) -> GraphRelation:
    return service.upsert(request)

