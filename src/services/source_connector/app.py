from fastapi import FastAPI

from services.common.models import HealthResponse, SourceRegistration
from services.common.storage import SqliteStore
from services.source_connector.config import Settings
from services.source_connector.core import SourceConnectorService

settings = Settings()
store = SqliteStore(settings.database_url)
service = SourceConnectorService(store)
app = FastAPI(title=settings.service_name)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(service=settings.service_name)


@app.post("/sources/register")
def register_source(payload: SourceRegistration) -> dict[str, str]:
    return service.register(payload)

