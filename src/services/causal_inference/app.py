from fastapi import FastAPI

from services.causal_inference.config import Settings
from services.causal_inference.core import CausalInferenceService
from services.common.models import CausalRequest, CausalResponse, HealthResponse
from services.common.storage import SqliteStore

settings = Settings()
store = SqliteStore(settings.graph_database_url)
service = CausalInferenceService(store)
app = FastAPI(title=settings.service_name)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(service=settings.service_name)


@app.post("/causal/infer", response_model=CausalResponse)
def infer(request: CausalRequest) -> CausalResponse:
    return service.infer(request)

