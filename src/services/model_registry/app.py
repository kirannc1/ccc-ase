from fastapi import FastAPI, HTTPException

from services.common.models import HealthResponse, ModelRegistrationRequest
from services.model_registry.config import Settings
from services.model_registry.core import ModelRegistryService

settings = Settings()
service = ModelRegistryService()
app = FastAPI(title=settings.service_name)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(service=settings.service_name)


@app.post("/models")
def register_model(request: ModelRegistrationRequest):
    return service.register(request).model_dump()


@app.post("/models/{model_id}/{version}/activate")
def activate(model_id: str, version: str):
    try:
        return service.activate(model_id, version).model_dump()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/models/{model_id}/{version}/deactivate")
def deactivate(model_id: str, version: str):
    try:
        return service.deactivate(model_id, version).model_dump()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/models/{model_id}")
def lookup(model_id: str, version: str | None = None):
    record = service.lookup(model_id, version)
    if record is None:
        raise HTTPException(status_code=404, detail="not found")
    return record.model_dump()

