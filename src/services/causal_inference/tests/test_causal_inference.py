from services.causal_inference.core import CausalInferenceService
from services.common.models import CausalRequest
from services.common.storage import SqliteStore


def test_causal_inference(tmp_path):
    store = SqliteStore(str(tmp_path / "graph.db"))
    store.executescript(
        """
        create table if not exists graph_node (
          node_id text primary key,
          tenant_id text not null,
          node_type text not null,
          source_entity_id text not null,
          created_at text default current_timestamp
        );
        create table if not exists graph_relation (
          relation_id integer primary key autoincrement,
          tenant_id text not null,
          from_node_id text not null,
          to_node_id text not null,
          relation_type text not null,
          evidence_class text not null,
          confidence real not null
        );
        """
    )
    store.execute(
        "insert into graph_relation (tenant_id, from_node_id, to_node_id, relation_type, evidence_class, confidence) values (?, ?, ?, ?, ?, ?)",
        ("tenant-a", "ent-1", "ent-2", "influences", "observed", 0.9),
    )
    service = CausalInferenceService(store)
    result = service.infer(CausalRequest(tenant_id="tenant-a", source_entity_id="ent-1", target_entity_id="ent-2"))
    assert result.confidence == 0.9

