from fastapi import FastAPI

from services.common.models import HealthResponse, OptimizationRequest
from services.optimization.config import Settings
from services.optimization.core import OptimizationService

settings = Settings()
service = OptimizationService()
app = FastAPI(title=settings.service_name)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(service=settings.service_name)


@app.post("/optimization/rank")
def rank(request: OptimizationRequest):
    return service.optimize(request).model_dump()

