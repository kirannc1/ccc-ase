from services.batch_ingestion.core import BatchIngestionService
from services.common.models import CanonicalEvent, EntityLink, FeatureGenerationRequest, GraphWriteRequest, RawRecord
from services.common.storage import SqliteStore
from services.entity_resolution.core import EntityResolutionService
from services.feature_engineering.core import FeatureEngineeringService
from services.knowledge_graph.core import KnowledgeGraphService
from services.semantic_normalization.core import SemanticNormalizationService


def test_core_processing_flow(tmp_path):
    batch_store = SqliteStore(str(tmp_path / "batch.db"))
    norm_store = SqliteStore(str(tmp_path / "norm.db"))
    entity_store = SqliteStore(str(tmp_path / "entity.db"))
    feature_store = SqliteStore(str(tmp_path / "feature.db"))
    graph_store = SqliteStore(str(tmp_path / "graph.db"))

    batch = BatchIngestionService(batch_store)
    normalizer = SemanticNormalizationService(norm_store)
    resolver = EntityResolutionService(entity_store)
    features = FeatureEngineeringService(feature_store)
    graph = KnowledgeGraphService(graph_store)

    raw = RawRecord(tenant_id="t1", source_system="workday", source_record_id="r1", payload={"team": "payments"})
    assert batch.ingest(raw)["status"] == "ingested"

    canonical = normalizer.normalize(raw)
    assert isinstance(canonical, CanonicalEvent)

    entity = resolver.resolve(canonical)
    assert isinstance(entity, EntityLink)

    feature = features.generate(FeatureGenerationRequest(event=canonical, entity=entity))
    relation = graph.upsert(GraphWriteRequest(entity=entity, feature=feature))
    assert relation.relation_type == "observes"
