from fastapi import FastAPI

from services.batch_ingestion.config import Settings
from services.batch_ingestion.core import BatchIngestionService
from services.common.models import HealthResponse, RawRecord
from services.common.storage import SqliteStore

settings = Settings()
store = SqliteStore(settings.database_url)
service = BatchIngestionService(store)
app = FastAPI(title=settings.service_name)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(service=settings.service_name)


@app.post("/ingest")
def ingest(record: RawRecord) -> dict[str, str]:
    return service.ingest(record)

