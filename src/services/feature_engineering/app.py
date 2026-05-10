from fastapi import FastAPI

from services.common.models import FeatureGenerationRequest, FeatureRecord, HealthResponse
from services.common.storage import SqliteStore
from services.feature_engineering.config import Settings
from services.feature_engineering.core import FeatureEngineeringService

settings = Settings()
store = SqliteStore(settings.database_url)
service = FeatureEngineeringService(store)
app = FastAPI(title=settings.service_name)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(service=settings.service_name)


@app.post("/features/generate", response_model=FeatureRecord)
def generate(request: FeatureGenerationRequest) -> FeatureRecord:
    return service.generate(request)

