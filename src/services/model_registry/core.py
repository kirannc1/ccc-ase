from services.common.models import ModelMetadata, ModelRegistrationRequest
from services.workflow_support import AuditRepository, InMemoryAuditRepository, InMemoryModelRegistryRepository, ModelRegistryRepository, new_id, utc_now
from services.common.models import AuditEvent


class ModelRegistryService:
    def __init__(self, repository: ModelRegistryRepository | None = None, audit: AuditRepository | None = None) -> None:
        self.repository = repository or InMemoryModelRegistryRepository()
        self.audit = audit or InMemoryAuditRepository()

    def register(self, request: ModelRegistrationRequest) -> ModelMetadata:
        metadata = ModelMetadata(model_id=request.model_id, name=request.name, version=request.version, config=request.config, status=request.status)
        self.repository.save(metadata)
        self.audit.append(AuditEvent(event_id=new_id("evt"), tenant_id="system", correlation_id=request.model_id, event_type="model.registered", resource_id=request.model_id, payload=metadata.model_dump()))
        return metadata.model_copy(deep=True)

    def activate(self, model_id: str, version: str) -> ModelMetadata:
        metadata = self.repository.get(model_id, version)
        if metadata is None:
            raise KeyError(model_id)
        metadata.status = "ACTIVE"
        metadata.updated_at = utc_now()
        self.repository.save(metadata)
        return metadata.model_copy(deep=True)

    def deactivate(self, model_id: str, version: str) -> ModelMetadata:
        metadata = self.repository.get(model_id, version)
        if metadata is None:
            raise KeyError(model_id)
        metadata.status = "INACTIVE"
        metadata.updated_at = utc_now()
        self.repository.save(metadata)
        return metadata.model_copy(deep=True)

    def lookup(self, model_id: str, version: str | None = None) -> ModelMetadata | None:
        metadata = self.repository.get(model_id, version)
        return metadata.model_copy(deep=True) if metadata else None
