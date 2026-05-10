from services.common.models import ModelRegistrationRequest
from services.model_registry.core import ModelRegistryService
from services.workflow_support import InMemoryAuditRepository, InMemoryModelRegistryRepository


def test_model_registry_activation_cycle():
    service = ModelRegistryService(InMemoryModelRegistryRepository(), InMemoryAuditRepository())
    metadata = service.register(ModelRegistrationRequest(model_id="m1", name="baseline", version="v1"))
    activated = service.activate("m1", "v1")
    deactivated = service.deactivate("m1", "v1")
    assert metadata.model_id == "m1"
    assert activated.status == "ACTIVE"
    assert deactivated.status == "INACTIVE"


def test_model_registry_lookup_missing():
    service = ModelRegistryService(InMemoryModelRegistryRepository(), InMemoryAuditRepository())
    assert service.lookup("missing") is None

