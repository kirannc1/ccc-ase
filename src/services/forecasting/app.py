from fastapi import FastAPI

from services.common.models import ForecastRequest, ForecastResponse, HealthResponse
from services.common.storage import SqliteStore
from services.forecasting.config import Settings
from services.forecasting.core import ForecastingService

settings = Settings()
store = SqliteStore(settings.feature_database_url)
service = ForecastingService(store)
app = FastAPI(title=settings.service_name)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(service=settings.service_name)


@app.post("/forecast", response_model=ForecastResponse)
def forecast(request: ForecastRequest) -> ForecastResponse:
    return service.forecast(request)

