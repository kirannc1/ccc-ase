from fastapi import FastAPI

from services.common.models import HealthResponse, ScenarioSimulationRequest
from services.scenario_simulation.config import Settings
from services.scenario_simulation.core import ScenarioSimulationService

settings = Settings()
service = ScenarioSimulationService()
app = FastAPI(title=settings.service_name)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(service=settings.service_name)


@app.post("/scenario/simulate")
def simulate(request: ScenarioSimulationRequest):
    return {"tenant_id": request.tenant_id, "scenarios": [scenario.model_dump() for scenario in service.simulate(request)]}

