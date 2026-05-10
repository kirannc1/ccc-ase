from fastapi import FastAPI, HTTPException

from services.audit_trail.config import Settings
from services.audit_trail.core import AuditTrailService
from services.common.models import AuditEvent, HealthResponse, ReplayRequest

settings = Settings()
service = AuditTrailService()
app = FastAPI(title=settings.service_name)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(service=settings.service_name)


@app.post("/audit/events")
def append_event(event: AuditEvent):
    return service.record(event).model_dump()


@app.post("/audit/replay")
def replay(request: ReplayRequest):
    return service.replay(request).model_dump()


@app.get("/audit/events/{event_id}")
def get_event(event_id: str):
    event = service.repository.get(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="not found")
    return event.model_dump()

