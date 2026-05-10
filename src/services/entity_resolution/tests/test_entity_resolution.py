from services.common.models import CanonicalEvent
from services.common.storage import SqliteStore
from services.entity_resolution.core import EntityResolutionService


def test_entity_resolution(tmp_path):
    store = SqliteStore(str(tmp_path / "entity.db"))
    service = EntityResolutionService(store)
    link = service.resolve(
        CanonicalEvent(
            event_id="evt_1",
            event_type="workday.normalized",
            tenant_id="t1",
            domain="hr",
            payload={},
            provenance={"source_record_id": "r1", "source_system": "workday"},
        )
    )
    assert link.entity_type == "team"
    row = store.fetch_one("select entity_id from entity_link where source_entity_id = ?", ("r1",))
    assert row["entity_id"] == link.entity_id

