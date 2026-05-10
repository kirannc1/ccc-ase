from fastapi import FastAPI, HTTPException

from services.common.models import HealthResponse, OverrideRequest
from services.human_override.config import Settings
from services.workflow_services import HumanOverrideService

settings = Settings()
service = HumanOverrideService()
app = FastAPI(title=settings.service_name)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(service=settings.service_name)


@app.post("/overrides")
def create_override(request: OverrideRequest):
    return service.apply(request).model_dump()


@app.get("/overrides/{decision_id}")
def get_override(decision_id: str):
    record = service.repository.get_by_decision(decision_id)
    if record is None:
        raise HTTPException(status_code=404, detail="not found")
    return record.model_dump()

