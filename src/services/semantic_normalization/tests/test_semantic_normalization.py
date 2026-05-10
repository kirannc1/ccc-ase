from services.common.models import RawRecord
from services.common.storage import SqliteStore
from services.semantic_normalization.core import SemanticNormalizationService


def test_normalize_record(tmp_path):
    store = SqliteStore(str(tmp_path / "normalize.db"))
    service = SemanticNormalizationService(store)
    event = service.normalize(
        RawRecord(tenant_id="t1", source_system="workday", source_record_id="r1", payload={"team": "payments"})
    )
    assert event.domain == "hr"
    row = store.fetch_one("select domain from canonical_event where event_id = ?", (event.event_id,))
    assert row["domain"] == "hr"

