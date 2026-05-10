from fastapi import FastAPI

from services.common.models import CanonicalEvent, HealthResponse, RawRecord
from services.common.storage import SqliteStore
from services.semantic_normalization.config import Settings
from services.semantic_normalization.core import SemanticNormalizationService

settings = Settings()
store = SqliteStore(settings.database_url)
service = SemanticNormalizationService(store)
app = FastAPI(title=settings.service_name)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(service=settings.service_name)


@app.post("/normalize", response_model=CanonicalEvent)
def normalize(record: RawRecord) -> CanonicalEvent:
    return service.normalize(record)

