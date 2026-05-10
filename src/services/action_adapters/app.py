from fastapi import FastAPI, HTTPException

from services.action_adapters.config import Settings
from services.common.models import ActionExecutionRequest, HealthResponse
from services.action_adapters.core import ActionAdaptersService

settings = Settings()
service = ActionAdaptersService()
app = FastAPI(title=settings.service_name)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(service=settings.service_name)


@app.get("/adapters")
def adapters():
    return {"adapters": service.list_adapters()}


@app.post("/adapters/{adapter_name}/execute")
def execute(adapter_name: str, request: ActionExecutionRequest):
    try:
        return service.execute(adapter_name, request)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

