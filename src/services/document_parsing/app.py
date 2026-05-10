from fastapi import FastAPI

from services.common.models import HealthResponse, ParsedDocument
from services.common.storage import SqliteStore
from services.document_parsing.config import Settings
from services.document_parsing.core import DocumentParsingService

settings = Settings()
store = SqliteStore(settings.database_url)
service = DocumentParsingService(store)
app = FastAPI(title=settings.service_name)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(service=settings.service_name)


@app.post("/parse")
def parse(document: ParsedDocument) -> dict[str, str]:
    return service.parse(document)

