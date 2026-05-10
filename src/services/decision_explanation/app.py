from fastapi import FastAPI

from services.common.models import ExplanationRequest, HealthResponse
from services.decision_explanation.config import Settings
from services.decision_explanation.core import DecisionExplanationService

settings = Settings()
service = DecisionExplanationService()
app = FastAPI(title=settings.service_name)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(service=settings.service_name)


@app.post("/explanation/generate")
def generate(request: ExplanationRequest):
    return service.explain(request).model_dump()

