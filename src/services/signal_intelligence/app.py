from fastapi import FastAPI

from services.common.models import HealthResponse, SignalIntelligenceRequest, SignalIntelligenceResponse
from services.common.storage import SqliteStore
from services.signal_intelligence.config import Settings
from services.signal_intelligence.core import SignalIntelligenceService

settings = Settings()
store = SqliteStore(settings.feature_database_url)
service = SignalIntelligenceService(store)
app = FastAPI(title=settings.service_name)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(service=settings.service_name)


@app.post("/signals/score", response_model=SignalIntelligenceResponse)
def score(request: SignalIntelligenceRequest) -> SignalIntelligenceResponse:
    return service.score(request.tenant_id, request.top_n)

