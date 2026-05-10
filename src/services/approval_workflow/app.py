from fastapi import FastAPI, HTTPException

from services.approval_workflow.config import Settings
from services.common.models import ApprovalRequest, ApprovalTransitionRequest, HealthResponse
from services.workflow_services import ApprovalWorkflowService

settings = Settings()
service = ApprovalWorkflowService()
app = FastAPI(title=settings.service_name)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(service=settings.service_name)


@app.post("/approvals")
def create_approval(request: ApprovalRequest):
    return service.start(request).model_dump()


@app.post("/approvals/{approval_id}/transition")
def transition_approval(approval_id: str, request: ApprovalTransitionRequest):
    if approval_id != request.approval_id:
        raise HTTPException(status_code=400, detail="approval_id mismatch")
    return service.transition(request).model_dump()


@app.get("/approvals/{approval_id}")
def get_approval(approval_id: str):
    record = service.repository.get(approval_id)
    if record is None:
        raise HTTPException(status_code=404, detail="not found")
    return record.model_dump()

