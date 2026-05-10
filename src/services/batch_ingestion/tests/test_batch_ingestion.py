from services.batch_ingestion.core import BatchIngestionService
from services.common.models import RawRecord
from services.common.storage import SqliteStore


def test_batch_ingest(tmp_path):
    store = SqliteStore(str(tmp_path / "batch.db"))
    service = BatchIngestionService(store)
    record = RawRecord(
        tenant_id="t1",
        source_system="hrms",
        source_record_id="r1",
        payload={"engagement": 0.5},
    )
    result = service.ingest(record)
    assert result["status"] == "ingested"
    row = store.fetch_one("select tenant_id, source_system from raw_batch_ingestion where source_record_id = ?", ("r1",))
    assert row["tenant_id"] == "t1"

