from fastapi import FastAPI

from services.common.models import HealthResponse, PolicyRequest, PolicyResponse
from services.common.storage import SqliteStore
from services.policy_service.config import Settings
from services.policy_service.core import PolicyService

settings = Settings()
store = SqliteStore(settings.feature_database_url)
service = PolicyService(store)
app = FastAPI(title=settings.service_name)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(service=settings.service_name)


@app.post("/policy/evaluate", response_model=PolicyResponse)
def evaluate(request: PolicyRequest) -> PolicyResponse:
    return service.evaluate(request)

