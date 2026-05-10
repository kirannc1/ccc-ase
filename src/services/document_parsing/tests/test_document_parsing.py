from services.common.models import ParsedDocument
from services.common.storage import SqliteStore
from services.document_parsing.core import DocumentParsingService


def test_parse_document(tmp_path):
    store = SqliteStore(str(tmp_path / "doc.db"))
    service = DocumentParsingService(store)
    result = service.parse(
        ParsedDocument(
            tenant_id="t1",
            document_id="d1",
            document_type="pdf",
            extracted={"vendor": "acme"},
        )
    )
    assert result["status"] == "parsed"
    row = store.fetch_one("select document_id from parsed_document where document_id = ?", ("d1",))
    assert row["document_id"] == "d1"

