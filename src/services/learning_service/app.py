from fastapi import FastAPI

from services.common.models import AuditEvent, HealthResponse, LearningTelemetry
from services.learning_service.config import Settings
from services.learning_service.core import LearningService

settings = Settings()
service = LearningService()
app = FastAPI(title=settings.service_name)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(service=settings.service_name)


@app.post("/learning/ingest")
def ingest(telemetry: LearningTelemetry, audit_events: list[AuditEvent] | None = None):
    return service.ingest(telemetry, audit_events).model_dump()


@app.get("/learning/dataset")
def dataset(tenant_id: str | None = None):
    return {"records": [record.model_dump() for record in service.dataset(tenant_id)]}

