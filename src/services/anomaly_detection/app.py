from fastapi import FastAPI

from services.anomaly_detection.config import Settings
from services.anomaly_detection.core import AnomalyDetectionService
from services.common.models import AnomalyRequest, AnomalyResponse, HealthResponse
from services.common.storage import SqliteStore

settings = Settings()
store = SqliteStore(settings.feature_database_url)
service = AnomalyDetectionService(store)
app = FastAPI(title=settings.service_name)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(service=settings.service_name)


@app.post("/anomaly/check", response_model=AnomalyResponse)
def check(request: AnomalyRequest) -> AnomalyResponse:
    return service.detect(request)

