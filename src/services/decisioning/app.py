from fastapi import FastAPI

from services.common.models import DecisionRequest, HealthResponse
from services.decisioning.config import Settings
from services.decisioning.core import DecisioningService

settings = Settings()
service = DecisioningService()
app = FastAPI(title=settings.service_name)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(service=settings.service_name)


@app.post("/decision/resolve")
def resolve(request: DecisionRequest):
    return service.decide(request).model_dump()

