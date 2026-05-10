from fastapi import FastAPI

from services.common.models import CanonicalEvent, EntityLink, HealthResponse
from services.common.storage import SqliteStore
from services.entity_resolution.config import Settings
from services.entity_resolution.core import EntityResolutionService

settings = Settings()
store = SqliteStore(settings.database_url)
service = EntityResolutionService(store)
app = FastAPI(title=settings.service_name)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(service=settings.service_name)


@app.post("/resolve", response_model=EntityLink)
def resolve(event: CanonicalEvent) -> EntityLink:
    return service.resolve(event)

