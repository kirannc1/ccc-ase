from services.common.models import EntityLink, FeatureRecord, GraphWriteRequest
from services.common.storage import SqliteStore
from services.knowledge_graph.core import KnowledgeGraphService


def test_graph_upsert(tmp_path):
    store = SqliteStore(str(tmp_path / "graph.db"))
    service = KnowledgeGraphService(store)
    relation = service.upsert(
        GraphWriteRequest(
            entity=EntityLink(
                tenant_id="t1",
                source_entity_id="r1",
                entity_id="ent_1",
                entity_type="team",
            ),
            feature=FeatureRecord(
                tenant_id="t1",
                entity_id="ent_1",
                feature_name="hr_signal_strength",
                value=0.8,
            ),
        )
    )
    assert relation.relation_type == "observes"
    row = store.fetch_one("select relation_type from graph_relation where tenant_id = ?", ("t1",))
    assert row["relation_type"] == "observes"

