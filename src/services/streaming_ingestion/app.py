from fastapi import FastAPI

from services.common.models import HealthResponse, RawRecord
from services.common.storage import SqliteStore
from services.streaming_ingestion.config import Settings
from services.streaming_ingestion.core import StreamingIngestionService

settings = Settings()
store = SqliteStore(settings.database_url)
service = StreamingIngestionService(store)
app = FastAPI(title=settings.service_name)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(service=settings.service_name)


@app.post("/stream")
def stream(record: RawRecord) -> dict[str, str]:
    return service.publish(record)

