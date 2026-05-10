from services.common.models import SourceRegistration
from services.common.storage import SqliteStore
from services.source_connector.core import SourceConnectorService


def test_register_source(tmp_path):
    store = SqliteStore(str(tmp_path / "source.db"))
    service = SourceConnectorService(store)
    result = service.register(
        SourceRegistration(source_id="src_1", source_name="workday", source_type="api")
    )
    assert result["status"] == "registered"
    row = store.fetch_one("select source_id, source_name from source_registration where source_id = ?", ("src_1",))
    assert row["source_name"] == "workday"

