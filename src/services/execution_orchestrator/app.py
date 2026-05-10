from fastapi import FastAPI, HTTPException

from services.common.models import ActionExecutionRequest, HealthResponse
from services.execution_orchestrator.config import Settings
from services.workflow_services import ExecutionOrchestratorService

settings = Settings()
service = ExecutionOrchestratorService()
app = FastAPI(title=settings.service_name)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(service=settings.service_name)


@app.post("/execution/dispatch")
def dispatch(request: ActionExecutionRequest):
    try:
        return service.dispatch(request).model_dump()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/execution/{action_id}")
def get_execution(action_id: str):
    result = service.repository.get(action_id)
    if result is None:
        raise HTTPException(status_code=404, detail="not found")
    return result.model_dump()

