from services.common.models import RawRecord
from services.common.storage import SqliteStore
from services.streaming_ingestion.core import StreamingIngestionService


def test_stream_publish(tmp_path):
    store = SqliteStore(str(tmp_path / "stream.db"))
    service = StreamingIngestionService(store)
    result = service.publish(
        RawRecord(tenant_id="t1", source_system="eventhub", source_record_id="e1", payload={"value": 1})
    )
    assert result["status"] == "published"
    row = store.fetch_one("select source_record_id from streaming_event where source_record_id = ?", ("e1",))
    assert row["source_record_id"] == "e1"

