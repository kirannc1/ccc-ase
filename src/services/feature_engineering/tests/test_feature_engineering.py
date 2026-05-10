from services.common.models import CanonicalEvent, EntityLink, FeatureGenerationRequest
from services.common.storage import SqliteStore
from services.feature_engineering.core import FeatureEngineeringService


def test_generate_feature(tmp_path):
    store = SqliteStore(str(tmp_path / "feature.db"))
    service = FeatureEngineeringService(store)
    feature = service.generate(
        FeatureGenerationRequest(
            event=CanonicalEvent(
                event_id="evt_1",
                event_type="workday.normalized",
                tenant_id="t1",
                domain="hr",
                payload={"engagement": 0.5, "absenteeism": 1},
                provenance={"source_record_id": "r1", "source_system": "workday"},
            ),
            entity=EntityLink(
                tenant_id="t1",
                source_entity_id="r1",
                entity_id="ent_1",
                entity_type="team",
            ),
        )
    )
    assert feature.feature_name == "hr_signal_strength"
    row = store.fetch_one("select feature_name from feature_record where entity_id = ?", ("ent_1",))
    assert row["feature_name"] == "hr_signal_strength"

